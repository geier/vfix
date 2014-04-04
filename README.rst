Repairs a CardDAV collection online
===================================

**experimental** make sure you have a backup


can fix these errors:

 * missing UIDs (this is required for getting your collection working with vdirsyncer)
 * missing FN (formated name) properties (just an annoyance), they get reconstructed from the N (name) property
 * LABEL properties where '\n' where not properly escaped are repaired


Howto
=====
just run `python fvix.py`
