select itemNumber, [$PRCCD], IUNITS, IUM2, ICOMPO, LIST from dancik_items
               left join dancik_price on [$PRCCD] = PRCCD and LIST_NUM = "LP"
                                           and dancik_price.schemaName = 'WAN'

                  where isWAN = 1