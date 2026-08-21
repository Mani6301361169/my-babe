"""
Task Scheduler Service - Handles background tasks, reminders, and alarms
Uses APScheduler for scheduling recurring and one-time tasks
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class TaskSchedulerService:
    """Service for scheduling background tasks"""
    
    _instance = None  # Singleton instance
    
    def __new__(cls):
        """Ensure single instance (singleton pattern)"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize scheduler service"""
        if self._initialized:
            return
        
        self.scheduler = BackgroundScheduler()
        self.jobs = {}  # Track jobs by ID
        self._initialized = True
        
        logger.info('TaskSchedulerService initialized')
    
    def start(self) -> None:
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info('Scheduler started')
    
    def stop(self) -> None:
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info('Scheduler stopped')
    
    # ============================================================================
    # REMINDERS
    # ============================================================================
    
    def add_reminder(
        self,
        message: str,
        delay_seconds: int = None,
        scheduled_time: datetime = None,
        callback: Optional[Callable] = None,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a one-time reminder.
        
        Args:
            message: Reminder message
            delay_seconds: Seconds until reminder (if no scheduled_time)
            scheduled_time: Specific datetime for reminder
            callback: Optional callback function to execute
            job_id: Optional unique job ID
        
        Returns:
            Job details
        """
        try:
            job_id = job_id or f'reminder_{int(datetime.now().timestamp())}'
            
            # Determine trigger time
            if scheduled_time:
                trigger = DateTrigger(run_date=scheduled_time)
            elif delay_seconds:
                run_date = datetime.now() + timedelta(seconds=delay_seconds)
                trigger = DateTrigger(run_date=run_date)
            else:
                return {'success': False, 'error': 'Must provide delay_seconds or scheduled_time'}
            
            # Define job function
            def reminder_job():
                logger.info(f'Reminder: {message}')
                if callback:
                    callback(message)
            
            # Schedule job
            job = self.scheduler.add_job(
                reminder_job,
                trigger=trigger,
                id=job_id,
                name=f'Reminder: {message[:30]}',
                replace_existing=True
            )
            
            self.jobs[job_id] = {
                'type': 'reminder',
                'message': message,
                'scheduled_time': job.next_run_time,
                'status': 'scheduled'
            }
            
            logger.info(f'Reminder scheduled: {job_id}')
            
            return {
                'success': True,
                'job_id': job_id,
                'message': message,
                'scheduled_time': str(job.next_run_time)
            }
            
        except Exception as e:
            logger.error(f'Error scheduling reminder: {e}')
            return {'success': False, 'error': str(e)}
    
    def add_recurring_reminder(
        self,
        message: str,
        cron_expression: str,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a recurring reminder using cron expression.
        
        Args:
            message: Reminder message
            cron_expression: Cron expression (e.g., "0 9 * * *" for 9 AM daily)
            job_id: Optional unique job ID
        
        Returns:
            Job details
        """
        try:
            job_id = job_id or f'recurring_reminder_{int(datetime.now().timestamp())}'
            
            trigger = CronTrigger.from_crontab(cron_expression)
            
            def reminder_job():
                logger.info(f'Recurring reminder: {message}')
            
            job = self.scheduler.add_job(
                reminder_job,
                trigger=trigger,
                id=job_id,
                name=f'Recurring: {message[:30]}',
                replace_existing=True
            )
            
            self.jobs[job_id] = {
                'type': 'recurring_reminder',
                'message': message,
                'cron': cron_expression,
                'status': 'active'
            }
            
            logger.info(f'Recurring reminder scheduled: {job_id}')
            
            return {
                'success': True,
                'job_id': job_id,
                'message': message,
                'cron': cron_expression,
                'next_run': str(job.next_run_time)
            }
            
        except Exception as e:
            logger.error(f'Error scheduling recurring reminder: {e}')
            return {'success': False, 'error': str(e)}
    
    # ============================================================================
    # ALARMS
    # ============================================================================
    
    def add_alarm(
        self,
        alarm_time: datetime,
        label: str = 'Alarm',
        sound_file: Optional[str] = None,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an alarm.
        
        Args:
            alarm_time: Datetime for alarm
            label: Alarm label
            sound_file: Path to sound file to play
            job_id: Optional unique job ID
        
        Returns:
            Job details
        """
        try:
            job_id = job_id or f'alarm_{int(datetime.now().timestamp())}'
            
            trigger = DateTrigger(run_date=alarm_time)
            
            def alarm_job():
                logger.info(f'ALARM: {label}')
                if sound_file:
                    self._play_sound(sound_file)
            
            job = self.scheduler.add_job(
                alarm_job,
                trigger=trigger,
                id=job_id,
                name=f'Alarm: {label}',
                replace_existing=True
            )
            
            self.jobs[job_id] = {
                'type': 'alarm',
                'label': label,
                'alarm_time': alarm_time,
                'status': 'set'
            }
            
            logger.info(f'Alarm set: {job_id}')
            
            return {
                'success': True,
                'job_id': job_id,
                'label': label,
                'alarm_time': str(alarm_time)
            }
            
        except Exception as e:
            logger.error(f'Error setting alarm: {e}')
            return {'success': False, 'error': str(e)}
    
    def add_recurring_alarm(
        self,
        time_str: str,  # "HH:MM" format
        days: list = None,  # Days of week (0=Monday, 6=Sunday)
        label: str = 'Alarm',
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a recurring alarm.
        
        Args:
            time_str: Time in HH:MM format (e.g., "07:30")
            days: List of day numbers (0-6) or None for every day
            label: Alarm label
            job_id: Optional unique job ID
        
        Returns:
            Job details
        """
        try:
            job_id = job_id or f'recurring_alarm_{int(datetime.now().timestamp())}'
            
            # Parse time
            hour, minute = map(int, time_str.split(':'))
            
            # Build cron expression
            if days is None or len(days) == 7:
                cron_expr = f'{minute} {hour} * * *'  # Every day
            else:
                day_str = ','.join(str(d) for d in sorted(days))
                cron_expr = f'{minute} {hour} * * {day_str}'
            
            trigger = CronTrigger.from_crontab(cron_expr)
            
            def alarm_job():
                logger.info(f'Recurring ALARM: {label} at {time_str}')
            
            job = self.scheduler.add_job(
                alarm_job,
                trigger=trigger,
                id=job_id,
                name=f'Recurring Alarm: {label}',
                replace_existing=True
            )
            
            self.jobs[job_id] = {
                'type': 'recurring_alarm',
                'label': label,
                'time': time_str,
                'days': days,
                'status': 'active'
            }
            
            logger.info(f'Recurring alarm set: {job_id}')
            
            return {
                'success': True,
                'job_id': job_id,
                'label': label,
                'time': time_str,
                'next_run': str(job.next_run_time)
            }
            
        except Exception as e:
            logger.error(f'Error setting recurring alarm: {e}')
            return {'success': False, 'error': str(e)}
    
    # ============================================================================
    # JOB MANAGEMENT
    # ============================================================================
    
    def list_jobs(self) -> Dict[str, Any]:
        """Get list of scheduled jobs"""
        try:
            jobs_list = []
            for job in self.scheduler.get_jobs():
                jobs_list.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': str(job.next_run_time),
                    'trigger': str(job.trigger)
                })
            
            return {
                'success': True,
                'total_jobs': len(jobs_list),
                'jobs': jobs_list
            }
            
        except Exception as e:
            logger.error(f'Error listing jobs: {e}')
            return {'success': False, 'error': str(e)}
    
    def remove_job(self, job_id: str) -> Dict[str, Any]:
        """Remove a scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.jobs:
                del self.jobs[job_id]
            
            logger.info(f'Job removed: {job_id}')
            
            return {'success': True, 'message': f'Job {job_id} removed'}
            
        except Exception as e:
            logger.error(f'Error removing job: {e}')
            return {'success': False, 'error': str(e)}
    
    def pause_job(self, job_id: str) -> Dict[str, Any]:
        """Pause a scheduled job"""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                self.scheduler.pause_job(job_id)
                if job_id in self.jobs:
                    self.jobs[job_id]['status'] = 'paused'
                return {'success': True, 'message': f'Job {job_id} paused'}
            else:
                return {'success': False, 'error': f'Job {job_id} not found'}
                
        except Exception as e:
            logger.error(f'Error pausing job: {e}')
            return {'success': False, 'error': str(e)}
    
    def resume_job(self, job_id: str) -> Dict[str, Any]:
        """Resume a paused job"""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                self.scheduler.resume_job(job_id)
                if job_id in self.jobs:
                    self.jobs[job_id]['status'] = 'active'
                return {'success': True, 'message': f'Job {job_id} resumed'}
            else:
                return {'success': False, 'error': f'Job {job_id} not found'}
                
        except Exception as e:
            logger.error(f'Error resuming job: {e}')
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def _play_sound(sound_file: str) -> None:
        """Play a sound file"""
        try:
            import winsound
            winsound.Beep(1000, 500)  # Frequency, duration in ms
        except:
            logger.warning('Could not play sound')
