select * from items
left join main.item_hierarchy  on items.ITEMNUMBER = H_ITEMNUMBER
where imfgr not in ('INT', 'JON', 'ALA', 'TAN') and items.ITEMNUMBER  not like '%MISC%'
  and items.ITEMNUMBER not in ('ARMLABOUR')
