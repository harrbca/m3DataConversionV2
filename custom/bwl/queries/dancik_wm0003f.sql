WITH
    CombinedData as (

select 'BWL' as schemaName,
    W3WARE,
    W3SUBAREA,
    W3DESC,
    W3AREA,
    W3BCODPRTF,
    W3BCODPRTQ,
    W3STAGEIN,
    W3STAGEOUT,
    W3VNASTGIN,
    W3VNASTGOT

FROM dancik_bwl.WM0003F

UNION ALL

select 'WAN' as schemaName,
    W3WARE,
    W3SUBAREA,
    W3DESC,
    W3AREA,
    W3BCODPRTF,
    W3BCODPRTQ,
    W3STAGEIN,
    W3STAGEOUT,
    W3VNASTGIN,
    W3VNASTGOT

FROM dancik_wan.WM0003F
    )
select * from CombinedData