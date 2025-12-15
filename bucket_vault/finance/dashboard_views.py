from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import SummarySerializer


@api_view(['GET'])
def summary(request):
    """Dashboard summary: net worth + bucket totals"""

    # Dummy data - replace with real queries later
    total_networth = 1250345.00
    growth_total = 750000.00
    safety_total = 500345.00

    growth_pct = round((growth_total / total_networth) * 100, 1)
    safety_pct = round((safety_total / total_networth) * 100, 1)

    data = {
        'total_networth': total_networth,
        'growth_total': growth_total,
        'safety_total': safety_total,
        'growth_pct': growth_pct,
        'safety_pct': safety_pct
    }

    serializer = SummarySerializer(data)
    return Response(serializer.data)
