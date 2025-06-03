select dancik_rolls.itemNumber, dancik_items.INAME, dancik_items.INAME2, IPRODL, dancik_items.ICLAS1, dancik_items.ICLAS2, dancik_items.ICLAS3, ICOMPO, IUNITC, IUNITS, IUM2, "RWARE#", "RROLL#", RLOC1, RONHAN, RLASTC, RLRCTD, "R#CUTS", RUM, RSHADE, "RCODE@" from dancik_rolls
left join dancik_Items on dancik_rolls.itemNumber = dancik_items.ITEMNUMBER
where
    dancik_rolls.schemaName = 'WAN'
    and dancik_items.IPRODL not in ('SAM', 'SET','DSP', 'DIS')
    and dancik_items.IMFGR not in ('INT', 'JON', 'ALA', 'TAN', 'LEX')
    and ronhan <> 0
order by "RWARE#", dancik_rolls.itemNumber, "RROLL#", RLOC1, RLRCTD