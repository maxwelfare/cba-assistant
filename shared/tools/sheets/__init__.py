"""Monte Carlo teaching sheets written from a data file, run from the shared folder with its venv.

    script    generate a sheet (.xlsx and columns.tsv) from a data file, and compare it with an export
    importer  read a sheet on the owner's older layout into a data file, and replay one against its export
    inplace   diff, plan and snapshot for writing a new version into a delivered Google Sheet
    suite     the stored suite, one test a complaint-register row, on the synthetic data file beside it
    fill_down.gs  the Apps Script a sheet may carry to fill a changed row-16 formula down

Each runs as `.venv/bin/python -m tools.sheets.<module>`. The rules these tools serve, and the register the suite
tests, are `standards/presentation/sheets.md`.
"""
