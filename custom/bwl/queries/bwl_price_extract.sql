select itemNumber, [$PRCCD], IUNITS, LIST from dancik_items
               left join dancik_price on [$PRCCD] = PRCCD and LIST_NUM = "LP"
                                           and dancik_price.schemaName = 'BWL'

                  where isBwl = 1