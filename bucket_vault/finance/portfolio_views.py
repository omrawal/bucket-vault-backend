from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, \
    HTTP_500_INTERNAL_SERVER_ERROR, HTTP_204_NO_CONTENT

from .models import Portfolio
from .serializers import PortfolioSerializer


@api_view(['GET'])
def portfolios_list(request):
    """List all portfolios from database"""
    portfolios = Portfolio.objects.all()
    serializer = PortfolioSerializer(portfolios, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_portfolio_list(request):
    """List all portfolios"""
    try:
        portfolios = Portfolio.objects.all().values('id', 'name')
        return Response(portfolios)
    except Exception as e:
        return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def create_new_portfolio(request):
    """Create a new portfolio"""
    print(request.data)
    portfolio_name = request.data.get('name', None)
    portfolio_description = request.data.get('description', None)
    if portfolio_name:
        Portfolio.objects.create(
            name=portfolio_name,
            description=portfolio_description if portfolio_description else ""
        )
        return Response(status=HTTP_201_CREATED)
    else:
        return Response(status=HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_portfolio(request, portfolio_id):
    """Delete a portfolio by ID"""
    try:
        portfolio = Portfolio.objects.get(id=portfolio_id)
        portfolio.delete()
        return Response(status=HTTP_204_NO_CONTENT)
    except Portfolio.DoesNotExist:
        return Response({'error': 'Portfolio not found'}, status=HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

