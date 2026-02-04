"""Alert checking and notification tasks."""

import logging
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from .celery_app import celery_app
from ..config import get_settings
from ..models import Alert, Company, SurvivalScore, UserProfile

logger = logging.getLogger(__name__)
settings = get_settings()


def get_async_session():
    engine = create_async_engine(settings.database_url)
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@celery_app.task(name="app.tasks.alerts.check_alerts")
def check_alerts():
    """Check all active alerts and trigger notifications."""
    import asyncio
    return asyncio.run(_check_alerts_async())


async def _check_alerts_async():
    """Async implementation of alert checking."""
    logger.info("Checking alerts")

    async_session = get_async_session()
    triggered = 0

    async with async_session() as db:
        # Get all active alerts
        result = await db.execute(
            select(Alert).where(Alert.is_active == True)
        )
        alerts = result.scalars().all()

        for alert in alerts:
            try:
                should_trigger = await _evaluate_alert(db, alert)

                if should_trigger:
                    # Update alert
                    alert.last_triggered_at = datetime.utcnow().isoformat()
                    alert.trigger_count = (alert.trigger_count or 0) + 1

                    # Queue notification
                    send_alert_notification.delay(str(alert.id))
                    triggered += 1

            except Exception as e:
                logger.error(f"Error evaluating alert {alert.id}: {e}")

        await db.commit()

    logger.info(f"Alert check complete: {triggered} triggered")
    return {"checked": len(alerts), "triggered": triggered}


async def _evaluate_alert(db: AsyncSession, alert: Alert) -> bool:
    """Evaluate if an alert should trigger."""

    if alert.alert_type == "score_drop":
        if not alert.company_id:
            return False

        # Get latest score
        result = await db.execute(
            select(SurvivalScore)
            .where(SurvivalScore.company_id == alert.company_id)
            .order_by(SurvivalScore.score_date.desc())
            .limit(2)
        )
        scores = result.scalars().all()

        if len(scores) < 2:
            return False

        current = float(scores[0].total_score)
        previous = float(scores[1].total_score)
        change_pct = ((current - previous) / previous) * 100

        if alert.change_percent and change_pct <= -float(alert.change_percent):
            return True

    elif alert.alert_type == "threshold":
        if not alert.company_id or not alert.threshold_value:
            return False

        result = await db.execute(
            select(SurvivalScore)
            .where(SurvivalScore.company_id == alert.company_id)
            .order_by(SurvivalScore.score_date.desc())
            .limit(1)
        )
        score = result.scalar_one_or_none()

        if not score:
            return False

        current = float(score.total_score)
        threshold = float(alert.threshold_value)

        if alert.threshold_direction == "below" and current < threshold:
            return True
        elif alert.threshold_direction == "above" and current > threshold:
            return True

    elif alert.alert_type == "score_rise":
        if not alert.company_id:
            return False

        result = await db.execute(
            select(SurvivalScore)
            .where(SurvivalScore.company_id == alert.company_id)
            .order_by(SurvivalScore.score_date.desc())
            .limit(2)
        )
        scores = result.scalars().all()

        if len(scores) < 2:
            return False

        current = float(scores[0].total_score)
        previous = float(scores[1].total_score)
        change_pct = ((current - previous) / previous) * 100

        if alert.change_percent and change_pct >= float(alert.change_percent):
            return True

    return False


@celery_app.task(name="app.tasks.alerts.send_alert_notification")
def send_alert_notification(alert_id: str):
    """Send notification for a triggered alert."""
    import asyncio
    return asyncio.run(_send_alert_notification_async(alert_id))


async def _send_alert_notification_async(alert_id: str):
    """Async implementation of alert notification."""
    logger.info(f"Sending notification for alert {alert_id}")

    async_session = get_async_session()

    async with async_session() as db:
        result = await db.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        alert = result.scalar_one_or_none()

        if not alert:
            return {"error": "Alert not found"}

        # Get user
        user_result = await db.execute(
            select(UserProfile).where(UserProfile.id == alert.user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            return {"error": "User not found"}

        # Get company info if applicable
        company_ticker = None
        if alert.company_id:
            company_result = await db.execute(
                select(Company).where(Company.id == alert.company_id)
            )
            company = company_result.scalar_one_or_none()
            if company:
                company_ticker = company.ticker

        # Send notifications based on preferences
        if alert.notify_email and user.email:
            # TODO: Integrate with email service (SendGrid, etc.)
            logger.info(f"Would send email to {user.email} for {company_ticker}")

        if alert.notify_push:
            # TODO: Integrate with push notification service
            logger.info(f"Would send push notification for {company_ticker}")

    return {"status": "sent", "alert_id": alert_id}
