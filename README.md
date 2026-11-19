# Boomerang Meter

[Compare Canadian anchor directions](https://coolcode.ca/boomerang-meter/)

Explore completed, public IPv4 traceroutes between Canadian RIPE Atlas anchors during a fixed two-hour UTC window. Filter by source, destination and exchange evidence, then inspect one direction’s count, denominator and original measurements. Export the selected groups to CSV. The detail compares the same direction with the preceding stored sample and links directly to that date. Each filter and direction is shareable.

<!-- coolcode:guide -->
On November 18, 2026 all eight completed traces from Beauharnois AS16276 to Vancouver AS396993 matched a DE-CIX New York member interface. The eight reverse traces reached Beauharnois with no exchange match. Compare the directions and open their original Atlas results.
<!-- /coolcode:guide -->

The launch covers 7,545 existing observations across October 4, November 11 and November 18, 2026. It uses a fixed panel of 20 operational Canadian anchors with public IPv4 mesh destination measurements identified during the November 19 review. The panel is listed in `scripts/anchors.json`. An absent pair means a sampled time window did not yield records for that direction. The panel omits users’ home connections. Do not generalize its fractions to Canadian internet traffic.

For each destination the collector reads the published Atlas mesh results for this panel from 18:00 to 20:00 UTC. It deduplicates by source probe and measurement timestamp within the destination file. A trace reaches its target if a responding address matches the recorded destination. Only reached traces enter the displayed country-match rates. The full observed and reached denominators are provided.

On the same date the collector builds an address index from the CAIDA PeeringDB archive. It matches a responding public address to a unique named exchange/country combination with a listed operational member interface and facilities all in that one country. A response from the destination itself is excluded from the exchange comparisons. A trace may match both Canadian and US exchanges. A positive result is evidence tied to the reported interface and facility geography. Remote peering, incomplete directory entries, hidden hops and repeated responses limit physical-route inference. Negative results never establish that a path stayed within Canada.

[RIPE Atlas](https://atlas.ripe.net/) supplies the published traces. [CAIDA’s PeeringDB archive](https://www.caida.org/catalog/datasets/peeringdb/) supplies the matching day’s exchange directory. The application links the exact time interval, source probe and measurement for every group. Only grouped counts and exchange names are bundled. No probes are commissioned.

A daily workflow adds a sample from two days earlier, validates the source results, runs browser checks and preserves earlier editions. `python scripts/refresh.py --date YYYY-MM-DD` collects a past sample. `node --test tests/*.test.mjs`, `python -m unittest discover -s tests` and `python scripts/build.py` check and build the site offline.

## Archive citation

The CAIDA UCSD PeeringDB Dataset, 2026-10-04 to 2026-11-18 (launch editions). The application updates this date range as it gains samples. [Dataset record](https://www.caida.org/catalog/datasets/peeringdb/) · [Public data agreement](https://www.caida.org/about/legal/aua/caida_pub_aua.html) · [Report a publication using CAIDA data](https://www.caida.org/catalog/datasets/publications/report-publication/).
