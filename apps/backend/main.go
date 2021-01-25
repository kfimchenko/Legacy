package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io/ioutil"
)

var reestrPath = flag.String("reestr", "reestr", "Path to reestr json file")
var lat = flag.Float64("lat", 0, "Latitude")
var long = flag.Float64("long", 0, "Longitude")

func main() {
	flag.Parse()

	cultures := getCultures(*reestrPath)

	res, err := findCultureByCoords(cultures, truncate3precision(*lat), truncate3precision(*long))
	if err != nil {
		panic(err)
	}

	fmt.Printf("%+v \n", res)
}

func findCultureByCoords(all []CultureObject, lat float64, long float64) (CultureObject, error) {
	lat = truncate3precision(lat)
	long = truncate3precision(long)
	for _, c := range all {
		if len(c.Data.General.Address.MapPosition.Coordinates) < 2 {
			continue
		}

		reestrLat := truncate3precision(c.Data.General.Address.MapPosition.Coordinates[0])
		reestrLong := truncate3precision(c.Data.General.Address.MapPosition.Coordinates[1])

		if lat == reestrLat && long == reestrLong {
			return c, nil
		}
	}

	return CultureObject{}, errors.New("culture object not found")
}

func truncate3precision(num float64) float64 {
	return float64(int(num*1000)) / 1000
}

func getCultures(path string) []CultureObject {
	file, _ := ioutil.ReadFile(path)

	var cultures []CultureObject

	err := json.Unmarshal(file, &cultures)
	if err != nil {
		panic(err)
	}

	return cultures
}

type CultureObject struct {
	NativeId string `json:"nativeId"`
	Data     struct {
		General struct {
			Name       string `json:"name"`
			CreateDate string `json:"createDate"`
			Photo      struct {
				Url string `json:"url"`
			} `json:"photo"`
			Address struct {
				FullAddress string `json:"fullAddress"`
				MapPosition struct {
					Coordinates []float64 `json:"coordinates"`
				} `json:"mapPosition"`
			} `json:"address"`
		} `json:"general"`
	} `json:"data"`
}
