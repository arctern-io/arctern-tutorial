# Copyright (C) 2019-2020 Zilliz. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from arctern.util import save_png
from arctern.util.vega import vega_pointmap, vega_heatmap, vega_choroplethmap, vega_weighted_pointmap

from arctern_pyspark import register_funcs
from arctern_pyspark import heatmap
from arctern_pyspark import pointmap
from arctern_pyspark import choroplethmap
from arctern_pyspark import weighted_pointmap

from pyspark.sql import SparkSession

import os
data_path = 'file://' + os.path.dirname(os.path.abspath(__file__)) + '/../../data/0_5M_nyc_taxi_and_building.csv'

def draw_point_map(spark):
    # file 0_5M_nyc_build.csv is generated from New York taxi data and taxi zone shapefile. Data is available at the following URL: https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page
    df = spark.read.format("csv").option("header", True).option("delimiter", ",").schema(
        "VendorID string, tpep_pickup_datetime timestamp, tpep_dropoff_datetime timestamp, passenger_count long, trip_distance double, pickup_longitude double, pickup_latitude double, dropoff_longitude double, dropoff_latitude double, fare_amount double, tip_amount double, total_amount double, buildingid_pickup long, buildingid_dropoff long, buildingtext_pickup string, buildingtext_dropoff string").load(
        data_path).cache()
    df.show(20, False)
    df.createOrReplaceTempView("nyc_taxi")

    register_funcs(spark)
    res = spark.sql("select ST_Point(pickup_longitude, pickup_latitude) as point from nyc_taxi where ST_Within(ST_Point(pickup_longitude, pickup_latitude), ST_GeomFromText('POLYGON ((-73.998427 40.730309, -73.954348 40.730309, -73.954348 40.780816 ,-73.998427 40.780816, -73.998427 40.730309))'))")

    vega = vega_pointmap(1024, 896, [-73.998427, 40.730309, -73.954348, 40.780816], 3, "#2DEF4A", 0.5, "EPSG:4326")
    res = pointmap(vega, res)
    save_png(res, '/tmp/pointmap.png')

    spark.sql("show tables").show()
    spark.catalog.dropGlobalTempView("nyc_taxi")

def draw_weighted_point_map(spark):
    df = spark.read.format("csv").option("header", True).option("delimiter", ",").schema(
        "VendorID string, tpep_pickup_datetime timestamp, tpep_dropoff_datetime timestamp, passenger_count long, trip_distance double, pickup_longitude double, pickup_latitude double, dropoff_longitude double, dropoff_latitude double, fare_amount double, tip_amount double, total_amount double, buildingid_pickup long, buildingid_dropoff long, buildingtext_pickup string, buildingtext_dropoff string").load(
        data_path).cache()
    df.show(20, False)
    df.createOrReplaceTempView("nyc_taxi")

    register_funcs(spark)

    # single color and single stroke width
    res1 = spark.sql("select ST_Point(pickup_longitude, pickup_latitude) as point from nyc_taxi where ST_Within(ST_Point(pickup_longitude, pickup_latitude), ST_GeomFromText('POLYGON ((-73.998427 40.730309, -73.954348 40.730309, -73.954348 40.780816 ,-73.998427 40.780816, -73.998427 40.730309))'))")
    vega1 = vega_weighted_pointmap(1024, 896, [-73.998427, 40.730309, -73.954348, 40.780816], "#87CEEB", [0, 2], [5], 1.0, "EPSG:4326")
    res1 = weighted_pointmap(vega1, res1)
    save_png(res1, '/tmp/weighted_pointmap_0_0.png')

    # multiple color and single stroke width
    res2 = spark.sql("select ST_Point(pickup_longitude, pickup_latitude) as point, tip_amount as c from nyc_taxi where ST_Within(ST_Point(pickup_longitude, pickup_latitude), ST_GeomFromText('POLYGON ((-73.998427 40.730309, -73.954348 40.730309, -73.954348 40.780816 ,-73.998427 40.780816, -73.998427 40.730309))'))")
    vega2 = vega_weighted_pointmap(1024, 896, [-73.998427, 40.730309, -73.954348, 40.780816], "blue_to_red", [0, 2], [5], 1.0, "EPSG:4326")
    res2 = weighted_pointmap(vega2, res2)
    save_png(res2, '/tmp/weighted_pointmap_1_0.png')

    # single color and multiple stroke width
    res3 = spark.sql("select ST_Point(pickup_longitude, pickup_latitude) as point, fare_amount as s from nyc_taxi where ST_Within(ST_Point(pickup_longitude, pickup_latitude), ST_GeomFromText('POLYGON ((-73.998427 40.730309, -73.954348 40.730309, -73.954348 40.780816 ,-73.998427 40.780816, -73.998427 40.730309))'))")
    vega3 = vega_weighted_pointmap(1024, 896, [-73.998427, 40.730309, -73.954348, 40.780816], "#87CEEB", [0, 2], [0, 10], 1.0, "EPSG:4326")
    res3 = weighted_pointmap(vega3, res3)
    save_png(res3, '/tmp/weighted_pointmap_0_1.png')

    # multiple color and multiple stroke width
    res4 = spark.sql("select ST_Point(pickup_longitude, pickup_latitude) as point, tip_amount as c, fare_amount as s from nyc_taxi where ST_Within(ST_Point(pickup_longitude, pickup_latitude), ST_GeomFromText('POLYGON ((-73.998427 40.730309, -73.954348 40.730309, -73.954348 40.780816 ,-73.998427 40.780816, -73.998427 40.730309))'))")
    vega4 = vega_weighted_pointmap(1024, 896, [-73.998427, 40.730309, -73.954348, 40.780816], "blue_to_red", [0, 2], [0, 10], 1.0, "EPSG:4326")
    res4 = weighted_pointmap(vega4, res4)
    save_png(res4, '/tmp/weighted_pointmap_1_1.png')

    spark.sql("show tables").show()
    spark.catalog.dropGlobalTempView("nyc_taxi")

def draw_heat_map(spark):
    df = spark.read.format("csv").option("header", True).option("delimiter", ",").schema(
        "VendorID string, tpep_pickup_datetime timestamp, tpep_dropoff_datetime timestamp, passenger_count long, trip_distance double, pickup_longitude double, pickup_latitude double, dropoff_longitude double, dropoff_latitude double, fare_amount double, tip_amount double, total_amount double, buildingid_pickup long, buildingid_dropoff long, buildingtext_pickup string, buildingtext_dropoff string").load(
        data_path).cache()
    df.show(20, False)
    df.createOrReplaceTempView("nyc_taxi")

    register_funcs(spark)
    res = spark.sql("select ST_Point(pickup_longitude, pickup_latitude) as point, passenger_count as w from nyc_taxi where ST_Within(ST_Point(pickup_longitude, pickup_latitude),  ST_GeomFromText('POLYGON ((-73.998427 40.730309, -73.954348 40.730309, -73.954348 40.780816 ,-73.998427 40.780816, -73.998427 40.730309))'))")

    vega = vega_heatmap(1024, 896, [-73.998427, 40.730309, -73.954348, 40.780816], 10.0, 'EPSG:4326')
    res = heatmap(vega, res)
    save_png(res, '/tmp/heatmap.png')

    spark.sql("show tables").show()
    spark.catalog.dropGlobalTempView("nyc_taxi")

def draw_choropleth_map(spark):
    df = spark.read.format("csv").option("header", True).option("delimiter", ",").schema(
        "VendorID string, tpep_pickup_datetime timestamp, tpep_dropoff_datetime timestamp, passenger_count long, trip_distance double, pickup_longitude double, pickup_latitude double, dropoff_longitude double, dropoff_latitude double, fare_amount double, tip_amount double, total_amount double, buildingid_pickup long, buildingid_dropoff long, buildingtext_pickup string, buildingtext_dropoff string").load(
        data_path).cache()
    df.show(20, False)
    df.createOrReplaceTempView("nyc_taxi")

    res = spark.sql("select ST_GeomFromText(buildingtext_dropoff) as polygon, passenger_count as w from nyc_taxi where (buildingtext_dropoff!='')")

    vega = vega_choroplethmap(1900, 1410, [-73.994092, 40.753893, -73.977588, 40.759642], "blue_to_red", [2.5, 5], 1.0, 'EPSG:4326')
    res = choroplethmap(vega, res)
    save_png(res, '/tmp/choroplethmap.png')

    spark.sql("show tables").show()
    spark.catalog.dropGlobalTempView("nyc_taxi")


if __name__ == "__main__":
    spark_session = SparkSession \
        .builder \
        .appName("Python Testmap") \
        .getOrCreate()

    spark_session.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")

    draw_weighted_point_map(spark_session)
    draw_heat_map(spark_session)
    draw_point_map(spark_session)
    draw_choropleth_map(spark_session)
    spark_session.stop()
