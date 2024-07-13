# Cinematic impact

Creating a virtual environment:

```
python -m venv venv
source venv/bin/activate
```

Installing the package from the repository using:
```
pip install -r .
```

Testing style by pylint:
```
pip install pylint
pylint src/cinematic_impact_package
```
Current score: ```10```

Example of starting demonstration program:
```
python3 src/cinematic_impact_package/demo.py --basics basics_path --ratings ratings_path --akas akas_path --gdp gdp_path --pop pop_path --pc pc_path --countries "Poland" "Germany" --genres "Comedy"
```
Profiling:

```
python3 -m cProfile -o out/demo.pts src/cinematic_impact_package/demo.py ...
```
```
echo "sort tottime\nstats\nquit" | python -m pstats out/demo.pts > pstats_output.txt
```
```
snakeviz demo.pts
```

Launching tests with pytest:

```
pytest --cov=cinematic_impact_package.lib
```

Data used to the analysis:

https://datasets.imdbws.com/

https://data.worldbank.org/indicator/NY.GDP.MKTP.CD?skipRedirection=true

https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?skipRedirection=true

https://data.worldbank.org/indicator/SP.POP.TOTL?skipRedirection=true

