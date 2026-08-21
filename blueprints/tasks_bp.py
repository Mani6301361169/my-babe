"""
Tasks Blueprint - Handles background tasks, reminders, and alarms
Routes:
  POST /api/tasks/reminder - Create reminder
  POST /api/tasks/alarm - Create alarm
  GET /api/tasks/jobs - List scheduled jobs
  DELETE /api/tasks/jobs/{job_id} - Remove job
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from services.task_scheduler_service import TaskSchedulerService

bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')
logger = logging.getLogger(__name__)


@bp.before_app_request
def init_scheduler():
    """Initialize scheduler on first request"""
    if not hasattr(bp, 'scheduler'):
        bp.scheduler = TaskSchedulerService()
        bp.scheduler.start()


@bp.route('/reminder', methods=['POST'])
def create_reminder():
    """
    Create a reminder.
    
    Expected JSON:
    {
        "message": "Reminder text",
        "delay_seconds": 300 (OR)
        "scheduled_time": "2024-01-15T14:30:00" (ISO format),
        "job_id": "reminder_123" (optional)
    }
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'success': False, 'error': 'Missing message'}), 400
        
        message = data['message']
        delay_seconds = data.get('delay_seconds')
        scheduled_time_str = data.get('scheduled_time')
        job_id = data.get('job_id')
        
        # Parse scheduled_time if provided
        scheduled_time = None
        if scheduled_time_str:
            scheduled_time = datetime.fromisoformat(scheduled_time_str)
        
        # Get or create scheduler
        scheduler = TaskSchedulerService()
        
        result = scheduler.add_reminder(
            message=message,
            delay_seconds=delay_seconds,
            scheduled_time=scheduled_time,
            job_id=job_id
        )
        
        return jsonify(result), (200 if result['success'] else 400)
        
    except Exception as e:
        logger.error(f'Error creating reminder: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/reminder/recurring', methods=['POST'])
def create_recurring_reminder():
    """
    Create a recurring reminder.
    
    Expected JSON:
    {
        "message": "Reminder text",
        "cron": "0 9 * * *" (9 AM every day),
        "job_id": "recurring_reminder_123" (optional)
    }
    
    Cron format: minute hour day_of_month month day_of_week
    Common examples:
    - "0 9 * * *" - 9 AM every day
    - "0 */2 * * *" - Every 2 hours
    - "0 9 * * 1-5" - 9 AM weekdays only
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data or 'cron' not in data:
            return jsonify({'success': False, 'error': 'Missing message or cron'}), 400
        
        message = data['message']
        cron = data['cron']
        job_id = data.get('job_id')
        
        scheduler = TaskSchedulerService()
        
        result = scheduler.add_recurring_reminder(
            message=message,
            cron_expression=cron,
            job_id=job_id
        )
        
        return jsonify(result), (200 if result['success'] else 400)
        
    except Exception as e:
        logger.error(f'Error creating recurring reminder: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/alarm', methods=['POST'])
def create_alarm():
    """
    Create an alarm.
    
    Expected JSON:
    {
        "alarm_time": "2024-01-15T07:00:00" (ISO format),
        "label": "Wake up alarm" (optional),
        "job_id": "alarm_123" (optional)
    }
    """
    try:
        data = request.get_json()
        if not data or 'alarm_time' not in data:
            return jsonify({'success': False, 'error': 'Missing alarm_time'}), 400
        
        alarm_time_str = data['alarm_time']
        alarm_time = datetime.fromisoformat(alarm_time_str)
        label = data.get('label', 'Alarm')
        job_id = data.get('job_id')
        
        scheduler = TaskSchedulerService()
        
        result = scheduler.add_alarm(
            alarm_time=alarm_time,
            label=label,
            job_id=job_id
        )
        
        return jsonify(result), (200 if result['success'] else 400)
        
    except Exception as e:
        logger.error(f'Error creating alarm: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/alarm/recurring', methods=['POST'])
def create_recurring_alarm():
    """
    Create a recurring alarm.
    
    Expected JSON:
    {
        "time": "07:30" (HH:MM format),
        "days": [0, 1, 2, 3, 4] (0=Monday, 6=Sunday, optional - None for every day),
        "label": "Morning alarm" (optional),
        "job_id": "alarm_recurring_123" (optional)
    }
    """
    try:
        data = request.get_json()
        if not data or 'time' not in data:
            return jsonify({'success': False, 'error': 'Missing time'}), 400
        
        time_str = data['time']
        days = data.get('days')
        label = data.get('label', 'Alarm')
        job_id = data.get('job_id')
        
        scheduler = TaskSchedulerService()
        
        result = scheduler.add_recurring_alarm(
            time_str=time_str,
            days=days,
            label=label,
            job_id=job_id
        )
        
        return jsonify(result), (200 if result['success'] else 400)
        
    except Exception as e:
        logger.error(f'Error creating recurring alarm: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/jobs', methods=['GET'])
def list_jobs():
    """
    List all scheduled jobs.
    
    Returns:
    {
        "success": true,
        "total_jobs": 3,
        "jobs": [
            {
                "id": "reminder_123",
                "name": "Reminder: Meeting at 2 PM",
                "next_run_time": "2024-01-15T14:00:00",
                "trigger": "date[2024-01-15 14:00:00]"
            },
            ...
        ]
    }
    """
    try:
        scheduler = TaskSchedulerService()
        result = scheduler.list_jobs()
        return jsonify(result), (200 if result['success'] else 400)
    except Exception as e:
        logger.error(f'Error listing jobs: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/jobs/<job_id>', methods=['DELETE'])
def remove_job(job_id):
    """
    Remove a scheduled job.
    
    Returns:
    {
        "success": true,
        "message": "Job removed"
    }
    """
    try:
        scheduler = TaskSchedulerService()
        result = scheduler.remove_job(job_id)
        return jsonify(result), (200 if result['success'] else 400)
    except Exception as e:
        logger.error(f'Error removing job: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/jobs/<job_id>/pause', methods=['POST'])
def pause_job(job_id):
    """Pause a scheduled job"""
    try:
        scheduler = TaskSchedulerService()
        result = scheduler.pause_job(job_id)
        return jsonify(result), (200 if result['success'] else 400)
    except Exception as e:
        logger.error(f'Error pausing job: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/jobs/<job_id>/resume', methods=['POST'])
def resume_job(job_id):
    """Resume a paused job"""
    try:
        scheduler = TaskSchedulerService()
        result = scheduler.resume_job(job_id)
        return jsonify(result), (200 if result['success'] else 400)
    except Exception as e:
        logger.error(f'Error resuming job: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500
