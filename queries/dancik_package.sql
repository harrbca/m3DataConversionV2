select icompo,
       IWIDTH,
       IPACCD,
       "UM#@1" as UMF_1,
       "UM1@1" as UM1_1,
       "UM2@1" as UM2_1,

       "UM#@2" as UMF_2,
       "UM1@2" as UM1_2,
       "UM2@2" as UM2_2,

       "UM#@3" as UMF_3,
       "UM1@3" as UM1_3,
       "UM2@3" as UM2_3,

       "UM#@4" as UMF_4,
       "UM1@4" as UM1_4,
       "UM2@4" as UM2_4,

       "UM#@5" as UMF_5,
       "UM1@5" as UM1_5,
       "UM2@5" as UM2_5,

       "UM#@6" as UMF_6,
       "UM1@6" as UM1_6,
       "UM2@6" as UM2_6

 from items where itemNumber = ? and rtrim(ipaccd) <> ''