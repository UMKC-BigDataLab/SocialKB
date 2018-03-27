#!/bin/bash
echo ""
date
echo ""
/usr/bin/time -v ./evaluate-urls.py ../../dbs/evidence.20k.db ../output/10/0p/map.infr.evidence.20k.10.out.txt > ../output/10/0p/map.infr.evidence.20k.10.positiveMals.txt


echo ""
date
echo ""

/usr/bin/time -v ./evaluate-urls.py ../../dbs/evidence.20k.db ../output/10/0p/mar.infr.evidence.20k.10.out.txt > ../output/10/0p/mar.infr.evidence.20k.10.p0.8.positiveMals.txt
