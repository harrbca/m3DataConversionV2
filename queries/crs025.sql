select "$PRCCD" as IPRCCD, min("$DESC") as IPRCCD_description
from dancik_items
where "$PRCCD" is not null
group by IPRCCD
order by IPRCCD