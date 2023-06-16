import uvicorn
from fastapi import FastAPI, Body
import ee
import numpy as np
import pandas as pd
from pydantic import BaseModel, Json
from typing import Dict


class Item(BaseModel):
    coords: Json[Dict[str, float]]


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/api/v1.0/check-status")
async def root():
    return {"Alive": True}


@app.post("/api/getdata")
def getdata(lon = Body(embed=True), lat = Body(embed=True)):

    def calcMean(img):
        mean = img.reduceRegion(ee.Reducer.mean(), poi_geometry).get(band)
        return img.set('date', img.date().format()).set('mean', mean)

    service_account = ''
    credentials = ee.ServiceAccountCredentials(service_account, '.json')
    ee.Initialize(credentials)

    #band = 'temperature_2m'
    band = 'NDSI_Snow_Cover'
    #sensor = "ECMWF/ERA5_LAND/HOURLY"
    sensor = "MODIS/006/MOD10A1"
    StartDate = "2022-02-01"
    EndDate = "2022-02-07"
    poi_geometry = ee.Geometry.Point([lon, lat])
    col = ee.ImageCollection(sensor).filterDate(StartDate, EndDate).filterBounds(poi_geometry).map(calcMean)
    values = col.reduceColumns(ee.Reducer.toList(2), ['date', 'mean']).values().get(0)
    values_list = ee.List(values).getInfo()
    return values_list


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, log_level="info")
