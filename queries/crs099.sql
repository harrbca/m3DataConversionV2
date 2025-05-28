select imfgr || "LPROD#" as prodLine, min(lname) as lname from items
    group by prodLine
    order by prodLine