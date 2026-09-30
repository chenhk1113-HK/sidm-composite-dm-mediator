# SIDM Concerto Data Cache

Local cache for Nadler+ 2025 SIDM Concerto parametric catalogs (Zenodo:
https://zenodo.org/records/14933624, DOI: 10.5281/zenodo.14933624).

**NOT committed to git.** Files in this directory are downloaded on demand
by `scripts/v192_c_concerto_subhalo_cloud9.py` from the URLs listed below.

## Downloaded catalogs

- `MW416/MW416_parametric.tar` (2.8 MB, MW-mass host Halo416, SIDM MilkyWaySIDM)
  - URL: https://zenodo.org/records/14933624/files/MW_Halo416_MilkyWaySIDM_parametric.tar?download=1
  - Contains: parametric fits for 2489 SIDM subhalos (m_int, rc1, Rmax, etc.)

## Usage

```bash
python scripts/v192_c_concerto_subhalo_cloud9.py
```

The script will re-download the catalog if missing and extract it locally.

## License

Data is CC-BY 4.0 (Nadler+ 2025). Acknowledge use per Zenodo citation instructions.
