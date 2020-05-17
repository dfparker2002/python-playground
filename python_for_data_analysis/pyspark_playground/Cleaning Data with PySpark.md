# DataFrame details
## Intro to data cleaning with Apache Spark
> Q: Why perform data cleaning with Spark?<br>
> A: Problem with typical data systems:
>   * Performance
>   * Organizing data flow

> Q: Advantages of Spark?<br>
> A: Scalable, powerful framework for data handling
>   * Spark offers high performance.
>   * Spark allows orderly data flows.
>   * Spark can use strictly defined schemas while ingesting data.

## Spark schemas
- Define the format of a dataframe
- May contain various data types: strings, dates, integers, arrays
- Can filter the garbage data during import
- Improves read performance

!["spark-schema"](img/spark-schema.png)

### Defining a schema
Creating a defined schema helps with data quality and import performance.
```python
# Import the pyspark.sql.types library
import pyspark.sql.types

# Define a new schema using the StructType method
people_schema = StructType([
  # Define a StructField for each field
  StructField('name', StringType(), nullable=False),
  StructField('age', IntegerType(), nullable=False),
  StructField('city', StringType(), nullable=False)
])
```

## Immutability and lazy processing
### Lazy processing
Lazy processing operations will usually return in about the same amount of time
regardless of the actual quantity of data. Remember that this is due to Spark
not performing any transformations until an action is requested. 

```python
# Load the CSV file
aa_dfw_df = spark.read.format('csv').options(Header=True).load('AA_DFW_2018.csv.gz')

# Add the airport column using the F.lower() method
aa_dfw_df = aa_dfw_df.withColumn('airport', F.lower(aa_dfw_df['Destination Airport']))

# Drop the Destination Airport column
aa_dfw_df = aa_dfw_df.drop(aa_dfw_df['Destination Airport'])

# Show the DataFrame
aa_dfw_df.show()
```

## Understanding Parquet
### The parquet format
!["parquet-format"](img/parquet-format.png)

### Working with parquet
!["read-write-parquet"](img/read-write-parquet.png)

### Parquet and SQL
The `Parquet` format is a columnar data store, allowing Spark to use predicate
pushdown. This means Spark will only process the data necessary to complete the
operations you define versus reading the entire dataset. This gives Spark more
flexibility in accessing the data and often drastically improves performance on
large datasets. 

!["parquet-and-sql"](img/parquet-and-sql.png)

# Manipulating DataFrames in the real world 
## Filtering column content with Python
```python
# Show the distinct VOTER_NAME entries
voter_df.select('VOTER_NAME').distinct().show(40, truncate=False)

# Filter voter_df where the VOTER_NAME is 1-20 characters in length
voter_df = voter_df.filter('length(VOTER_NAME) > 0 and length(VOTER_NAME) < 20')

# Filter out voter_df where the VOTER_NAME contains an underscore
voter_df = voter_df.filter(~ F.col('VOTER_NAME').contains('_'))

# Show the distinct VOTER_NAME entries again
voter_df.select('VOTER_NAME').distinct().show(40, truncate=False)
```

## Modifying DataFrame columns
```python
# Add a new column called splits separated on whitespace
voter_df = voter_df.withColumn('splits', F.split(voter_df.VOTER_NAME, '\s+'))

# Create a new column called first_name based on the first item in splits
voter_df = voter_df.withColumn('first_name', voter_df.splits.getItem(0))

# Get the last entry of the splits list and create a column called last_name
voter_df = voter_df.withColumn('last_name', voter_df.splits.getItem(F.size('splits') - 1))

# Drop the splits column
voter_df = voter_df.drop('splits')
```
## Conditional DataFrame column operations
- `.when(<if condition>, <then x>)`: lets you conditionally modify a Data Frame
based on its content.
- `.otherwise()` is like `else`

```python
# method 1
df.select(df.Name, df.Age,
          .when(df.Age >= 18, "Adult")
          .when(df.Age < 18, "Minor"))
# method 2
df.select(df.Name, df.Age,
          .when(df.Age >= 18, "Adult")
          .otherwise("Minor"))
```

```python
# Add a column to voter_df for a voter based on their position
voter_df = voter_df.withColumn('random_val',
                               when(voter_df.TITLE == 'Councilmember', F.rand())
                               .when(voter_df.TITLE == 'Mayor', 2)
                               .otherwise(0))
```

## User defined functions
!["user-defined-functions"](img/udf.png)

## Partitioning and lazy processing
```python
# Select all the unique council voters
voter_df = df.select(df["VOTER NAME"]).distinct()

# Count the rows in voter_df
print("\nThere are %d rows in the voter_df DataFrame.\n" % voter_df.count())

# Add a ROW_ID
voter_df = voter_df.withColumn('ROW_ID', F.monotonically_increasing_id())

# Show the rows with 10 highest IDs in the set
voter_df.orderBy(voter_df.ROW_ID.desc()).show(10)
```

To check the number of partitions, use the method `.rdd.getNumPartitions()`
on a DataFrame.

# Improving Performance
## Caching
> Q: What is caching?<br>
> A: Caching in Spark:
>   * Stores DataFrames in memory or on disk
>   * Improves speed on later transformations / actions
>   * Reduces resource usage

> Q: Disadvantages of caching<br>
>   * Very large data sets may not fit in memory
>   * Local disk based caching may not be a performance improvement
>   * Cached objects may not be available

Call `.cache()` on the DataFrame before Action:
```python
voter_df = voter_df.withColumn('ID', monotonically_increasing_id())
voter_df = voter_df.cache()
```

Check `.is_cached` to determine cache status:
```python
voter_df.is_cached
```

Call `.unpersist()` when finished with DataFrame:
```python
voter_df.unpersist()
```

## Improve import performance
Spark Clusters are made of two types of processes
- Driver process
- Worker processes

Important parameters:
- Number of objects (Files, Network locations, etc)
  * More objects better than larger ones
  * Can import via wildcard<br>
  `airport_df = spark.read.csv('airports-*.txt.gz')`
- General size of objects
  * Spark performs better if objects are of similar size

A well-de ned schema will drastically improve import performance
- Avoids reading the data multiple times
- Provides validation on import

## Cluster configurations
!["spark-cluster-driver"](img/spark-cluster-driver.png)
!["spark-cluster-worker"](img/spark-cluster-worker.png)

```python
# Check the name of the Spark application instance ('spark.app.name')
app_name = spark.conf.get('spark.app.name')

# Determine the TCP port the driver runs on ('spark.driver.port')
driver_tcp_port = spark.conf.get('spark.driver.port')

# Determine how many partitions are configured for joins
num_partitions = spark.conf.get('spark.sql.shuffle.partitions')
```

```python
# Store the number of partitions in variable
before = departures_df.rdd.getNumPartitions()

# Configure Spark to use 500 partitions
spark.conf.set('spark.sql.shuffle.partitions', 500)

# Recreate the DataFrame using the departures data file
departures_df = spark.read.csv('departures.txt.gz').distinct()

# Print the number of partitions for each instance
print("Partition count before change: %d" % before)
print("Partition count after change: %d" % departures_df.rdd.getNumPartitions())
```

## Performance improvements
> Q: What is shuffling?<br>
> A: Shuffling refers to moving data around to various workers to complete a task
>   * Hides complexity from the user
>   * Can be slow to complete
>   * Lowers overall throughput
>   * Is often necessary, but try to minimize

> Q: How to limit shuffling?<br>
> A:
>   * Limit use of `.repartition(num_partitions)`
>   * Use `.coalesce(num_partitions)` instead
>   * Use care when calling `.join()`
>   * Use `.broadcast()`
>   * May not need to limit it

### Using broadcasting on Spark joins
- Broadcast the smaller DataFrame. The larger the DataFrame, the more time
required to transfer to the worker nodes.
- On small DataFrames, it may be better skip broadcasting and let Spark figure
out any optimization on its own.
- If you look at the query execution plan, a broadcastHashJoin indicates you've
successfully configured broadcasting.

```python
from pyspark.sql.functions import broadcast

# Join the flights_df and airports_df DataFrames using broadcasting
broadcast_df = flights_df.join(broadcast(airports_df), \
    flights_df["Destination Airport"] == airports_df["IATA"] )
```








