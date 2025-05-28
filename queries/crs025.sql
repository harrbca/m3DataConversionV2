select "$PRCCD" as priceClass, min("$DESC") as description
from items
where "$PRCCD" is not null
group by priceClass
order by priceClass