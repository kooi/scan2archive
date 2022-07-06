# scan2archive

scan2archive is a paper backup facilitator. It consists of two parts:
- A cover sheet generator (in-browser; client-side) to generate a paper cover sheet containing human-readable text and concurrent machine readable qr;
- a scan interpreter to run within a nextcloud instance to automatically sort incoming recognized archive scans (containing a cover sheet).

## Status

 - Cover sheet generation is working (if with a somewhat ugly interface)
 - Scan interpretation currently works as a testing script.