from django.db.models import Sum, Count
from django.utils import timezone

from persistence.models import RevenueTracker


class RevenueMetrics(RevenueTracker):
    """
    Backward-compat proxy for code importing:
      from intelligence.models import RevenueMetrics
    Reuses the persistence.RevenueTracker table.
    """
    class Meta:
        proxy = True
        app_label = 'intelligence'
        verbose_name = 'Revenue Metrics'
        verbose_name_plural = 'Revenue Metrics'

    @classmethod
    def update_metrics_for_date(cls, date):
        """
        Calculate and return aggregated metrics for a specific date.
        This is a read-only aggregation - no data is modified.
        """
        from datetime import datetime, time

        # Get start and end of day
        if hasattr(date, 'date'):
            date = date.date()

        start_of_day = timezone.make_aware(datetime.combine(date, time.min))
        end_of_day = timezone.make_aware(datetime.combine(date, time.max))

        # Aggregate metrics for the date
        metrics = cls.objects.filter(
            created_at__gte=start_of_day,
            created_at__lte=end_of_day
        ).aggregate(
            total_amount=Sum('amount'),
            transaction_count=Count('id')
        )

        return {
            'date': str(date),
            'total_revenue': float(metrics['total_amount'] or 0),
            'transaction_count': metrics['transaction_count'] or 0,
        }


class EarningRecord(RevenueTracker):
    """
    Backward-compat proxy for:
      from intelligence.models import EarningRecord
    Same underlying table as RevenueTracker.
    """
    class Meta:
        proxy = True
        app_label = 'intelligence'
        verbose_name = 'Earning Record'
        verbose_name_plural = 'Earning Records'
