from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Portfolio
from .serializers import SummarySerializer
from .utils.portfolio_helper import calculate_total_networth


@api_view(['GET'])
def get_total_networth(request):
    """Get total networth across all portfolios"""
    try:
        total_networth = 0
        portfolio_id = request.query_params.get('portfolio_id', None)
        if portfolio_id:
            portfolio = Portfolio.objects.get(id=portfolio_id)
            total_networth = calculate_total_networth(portfolio)
            return Response(total_networth)
        else:
            return Response({'error': 'Portfolio ID not provided'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)