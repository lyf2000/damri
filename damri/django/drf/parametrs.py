from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

id_param = OpenApiParameter("id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY)
