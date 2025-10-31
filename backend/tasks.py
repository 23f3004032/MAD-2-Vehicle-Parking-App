#==============================================================================
#                           CELERY BACKGROUND TASKS
#                         Email Notifications & Data Export
#==============================================================================
# Description: Background tasks for email reminders, monthly reports, CSV export
# Features: Daily reminders, monthly reports, CSV export with email attachments
# Scheduling: Managed by Celery Beat with IST timezone support
#==============================================================================

from datetime import datetime, timedelta
import os
import csv
import pytz
from sqlalchemy import func
from flask import current_app
from flask_mail import Message
from extensions import db, mail, celery
from models import User, Lot, Spot, ReserveSpot

#==============================================================================
#                           TIMEZONE UTILITIES
#==============================================================================

#------India timezone configuration------#
INDIA_TZ = pytz.timezone('Asia/Kolkata')

def get_india_time():
    """Get current time in India timezone"""
    return datetime.now(INDIA_TZ)

def to_india_time(dt):
    """Convert datetime to India timezone"""
    if dt.tzinfo is None:
        return INDIA_TZ.localize(dt)
    return dt.astimezone(INDIA_TZ)

#==============================================================================
#                           EMAIL TEMPLATE SYSTEM
#==============================================================================

#------HTML email template generator------#
def create_email_template(subject, body_content, user_name="User"):
    """Create professional HTML email template"""
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .footer {{ padding: 10px; text-align: center; color: #666; }}
            .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .stat-box {{ background: white; padding: 15px; border-radius: 5px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>OnlyPark - {subject}</h1>
        </div>
        <div class="content">
            <h2>Hello {user_name}!</h2>
            {body_content}
        </div>
        <div class="footer">
            <p>Thank you for using OnlyPark!</p>
            <p>Generated on {get_india_time().strftime('%Y-%m-%d %H:%M IST')}</p>
        </div>
    </body>
    </html>
    """
    return html_template

#==============================================================================
#                           DAILY REMINDER SYSTEM
#==============================================================================

#------Scheduled daily reminder task------#
@celery.task
def send_daily_reminders():
    """
    Sends daily reminders based on project requirements, using IST for all time calculations.
    Priority 1: If new lots were created in the last 24 hours, notify ALL users.
    Priority 2: If no new lots, notify users who haven't parked in 7+ days.
    """
    try:
        # --- Priority 1: Check for newly created lots in the last 24 hours ---
        yesterday = get_india_time() - timedelta(days=1)
        new_lots = Lot.query.filter(Lot.created_at >= yesterday).all()

        if new_lots:
            all_users = User.query.filter_by(role='user').all()
            
            new_lots_html = "<ul>"
            for lot in new_lots:
                new_lots_html += f"<li><strong>{lot.name}</strong> - {lot.prime_location_name}</li>"
            new_lots_html += "</ul>"
            
            body_content = f"""
            <p>Great news! We've just added some new parking locations for you to check out:</p>
            {new_lots_html}
            <p>Why not book a spot for your next visit? We're ready when you are!</p>
            """
            
            emails_sent = 0
            for user in all_users:
                try:
                    html_content = create_email_template("New Parking Locations Available!", body_content, user.fullname)
                    msg = Message(
                        subject="OnlyPark - New Parking Locations Available!",
                        recipients=[user.email],
                        html=html_content
                    )
                    mail.send(msg)
                    emails_sent += 1
                except Exception as e:
                    pass  # Continue with other users if one fails
            
            return f"Notified {emails_sent} users about {len(new_lots)} new lots."

        # --- Priority 2: If no new lots, check for inactive users ---
        else:
            
            seven_days_ago = get_india_time() - timedelta(days=7)
            
            recent_user_ids = db.session.query(ReserveSpot.user_id)\
                .filter(ReserveSpot.parking_time >= seven_days_ago)\
                .distinct()

            inactive_users = User.query.filter(User.role == 'user', User.id.notin_(recent_user_ids)).all()

            if not inactive_users:
                return "No inactive users found. All users are actively using the service!"

            body_content = """
            <p>We miss you! It's been a while since your last parking booking.</p>
            <p>Don't forget that OnlyPark is here whenever you need convenient parking solutions.</p>
            <p>Check out our available spots and book your next parking session!</p>
            """

            emails_sent = 0
            for user in inactive_users:
                try:
                    html_content = create_email_template("We Miss You!", body_content, user.fullname)
                    msg = Message(
                        subject="OnlyPark - We Miss You!",
                        recipients=[user.email],
                        html=html_content
                    )
                    mail.send(msg)
                    emails_sent += 1
                except Exception as e:
                    pass  # Continue with other users if one fails

            return f"Sent reminder emails to {emails_sent} inactive users."

    except Exception as e:
        return f"Error sending daily reminders: {str(e)}"

#----------Monthly Report Task----------#
@celery.task
def generate_monthly_report(user_id):
    """Generate monthly activity report for a specific user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return f"User {user_id} not found"
        
        # Calculate date range for last month
        now = get_india_time()
        first_day_current_month = now.replace(day=1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)
        
        # Get reservations for last month
        month_reservations = ReserveSpot.query.filter(
            ReserveSpot.user_id == user_id,
            ReserveSpot.parking_time >= first_day_previous_month,
            ReserveSpot.parking_time <= last_day_previous_month
        ).all()
        
        if not month_reservations:
            return f"No reservations found for user {user_id} in {last_day_previous_month.strftime('%B %Y')}"
        
        # Calculate statistics
        total_reservations = len(month_reservations)
        completed_reservations = [r for r in month_reservations if r.leaving_time is not None]
        total_spent = sum(r.cost or 0 for r in completed_reservations)
        total_hours = 0
        
        # Calculate total hours
        for reservation in completed_reservations:
            if reservation.parking_time and reservation.leaving_time:
                duration = reservation.leaving_time - reservation.parking_time
                total_hours += duration.total_seconds() / 3600
        
        # Find most used lot
        lot_usage = {}
        for reservation in month_reservations:
            if reservation.spot and reservation.spot.lot:
                lot_name = reservation.spot.lot.name
                lot_usage[lot_name] = lot_usage.get(lot_name, 0) + 1
        
        most_used_lot = max(lot_usage.items(), key=lambda x: x[1]) if lot_usage else ("N/A", 0)
        
        # Create detailed reservations list
        reservations_details = ""
        for reservation in month_reservations:
            status = "Completed" if reservation.leaving_time else "Active"
            cost = f"₹{reservation.cost:.2f}" if reservation.cost else "₹0.00"
            spot_name = f"Spot {reservation.spot.spot_number}" if reservation.spot else "N/A"
            lot_name = reservation.spot.lot.name if reservation.spot and reservation.spot.lot else "N/A"
            
            reservations_details += f"""
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;">{reservation.vehicle_no}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{lot_name}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{spot_name}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{reservation.parking_time.strftime('%Y-%m-%d %H:%M')}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{status}</td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{cost}</td>
                </tr>
            """
        
        body_content = f"""
        <h3>📊 Your Monthly Parking Report - {last_day_previous_month.strftime('%B %Y')}</h3>
        
        <div class="stats">
            <div class="stat-box">
                <h4>Total Bookings</h4>
                <h2>{total_reservations}</h2>
            </div>
            <div class="stat-box">
                <h4>Total Spent</h4>
                <h2>₹{total_spent:.2f}</h2>
            </div>
            <div class="stat-box">
                <h4>Total Hours</h4>
                <h2>{total_hours:.1f}</h2>
            </div>
            <div class="stat-box">
                <h4>Favorite Location</h4>
                <h2>{most_used_lot[0]}</h2>
                <p>{most_used_lot[1]} visits</p>
            </div>
        </div>
        
        <h3>📋 Detailed Booking History</h3>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <thead>
                <tr style="background-color: #4CAF50; color: white;">
                    <th style="padding: 10px; border: 1px solid #ddd;">Vehicle</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Location</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Spot</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Date & Time</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Status</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">Cost</th>
                </tr>
            </thead>
            <tbody style="background-color: white;">
                {reservations_details}
            </tbody>
        </table>
        
        <p>Keep up the great parking habits! 🚗</p>
        """
        
        # Create and send email
        html_content = create_email_template("Monthly Activity Report", body_content, user.fullname)
        
        msg = Message(
            subject=f"OnlyPark - Monthly Report ({last_day_previous_month.strftime('%B %Y')})",
            recipients=[user.email],
            html=html_content
        )
        
        mail.send(msg)
        
        return f"Monthly report sent to {user.email}"
        
    except Exception as e:
        return f"Error generating monthly report for user {user_id}: {str(e)}"

@celery.task
def generate_all_monthly_reports():
    """Generate monthly reports for all users"""
    try:
        users = User.query.filter_by(role='user').all()
        reports_sent = 0
        
        for user in users:
            try:
                generate_monthly_report.delay(user.id)
                reports_sent += 1
            except Exception as e:
                pass  # Continue with other users if one fails
        
        return f"Monthly report generation initiated for {reports_sent} users"
        
    except Exception as e:
        return f"Error generating monthly reports: {str(e)}"

#----------CSV Export Task----------#
@celery.task
def export_user_data_csv(user_id, export_type='all'):
    """Export user data to CSV and email it"""
    try:
        user = User.query.get(user_id)
        if not user:
            return f"User {user_id} not found"
        
        # Create export directory if it doesn't exist
        export_dir = current_app.config.get('EXPORT_DIR', 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = get_india_time().strftime('%Y%m%d_%H%M%S')
        filename = f"parking_data_{user.id}_{timestamp}.csv"
        filepath = os.path.join(export_dir, filename)
        
        # Get user's reservations
        reservations = ReserveSpot.query.filter_by(user_id=user_id).all()
        
        if not reservations:
            return f"No reservations found for user {user_id}"
        
        # Create CSV file
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'Reservation ID', 'Vehicle Number', 'Parking Location', 'Spot Number',
                'Parking Time', 'Leaving Time', 'Duration (Hours)', 'Cost', 'Status'
            ])
            
            # Write reservation data
            for reservation in reservations:
                duration = ""
                if reservation.parking_time and reservation.leaving_time:
                    duration_delta = reservation.leaving_time - reservation.parking_time
                    duration = f"{duration_delta.total_seconds() / 3600:.2f}"
                
                status = "Completed" if reservation.leaving_time else "Active"
                lot_name = reservation.spot.lot.name if reservation.spot and reservation.spot.lot else "N/A"
                spot_number = f"Spot {reservation.spot.spot_number}" if reservation.spot else "N/A"  
                
                writer.writerow([
                    reservation.id,
                    reservation.vehicle_no,
                    lot_name,
                    spot_number,
                    reservation.parking_time.strftime('%Y-%m-%d %H:%M:%S') if reservation.parking_time else "",
                    reservation.leaving_time.strftime('%Y-%m-%d %H:%M:%S') if reservation.leaving_time else "",
                    duration,
                    f"₹{reservation.cost:.2f}" if reservation.cost else "₹0.00",
                    status
                ])
        
        # Email the CSV file
        body_content = f"""
        <p>Your parking data export is ready!</p>
        
        <div style="background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3>📊 Export Details</h3>
            <p><strong>Total Records:</strong> {len(reservations)}</p>
            <p><strong>Export Type:</strong> Complete parking history</p>
            <p><strong>Generated:</strong> {get_india_time().strftime('%Y-%m-%d %H:%M IST')}</p>
        </div>
        
        <p>The CSV file contains all your parking bookings with complete details including locations, timings, and costs.</p>
        <p>You can open this file in Excel or any spreadsheet application for further analysis.</p>
        """
        
        html_content = create_email_template("Data Export Ready", body_content, user.fullname)
        
        msg = Message(
            subject="OnlyPark - Your Data Export is Ready",
            recipients=[user.email],
            html=html_content
        )
        
        # Attach CSV file
        with open(filepath, 'rb') as f:
            msg.attach(filename, "text/csv", f.read())
        
        mail.send(msg)
        
        return f"CSV export sent to {user.email} with {len(reservations)} records"
        
    except Exception as e:
        return f"Error exporting data for user {user_id}: {str(e)}"