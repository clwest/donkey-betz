from persistence.models import SpiderData


class SpiderIntelligenceNode(SpiderData):
    """
    Proxy to keep backward compatibility with older imports like:
      from intelligence.models import SpiderIntelligenceNode

    This does not create a new table; it reuses persistence.SpiderData.
    """
    class Meta:
        proxy = True
        app_label = 'intelligence'
        verbose_name = 'Spider Intelligence Node'
        verbose_name_plural = 'Spider Intelligence Nodes'
