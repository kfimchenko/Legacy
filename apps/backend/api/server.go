package api

import (
	"encoding/json"
	"errors"
	"github.com/EatsLemons/Legacy/apps/backend/storage"
	"net/http"
	"strconv"
)

func FindByCoords(all []storage.Culture, w http.ResponseWriter, req *http.Request) {
	latParam, _ := req.URL.Query()["lat"]
	longParam, _ := req.URL.Query()["long"]

	lat, _ := strconv.ParseFloat(latParam[0], 64)
	long, _ := strconv.ParseFloat(longParam[0], 64)

	cultureObject, notFound := findCultureByCoords(all, lat, long)
	if notFound != nil {
		w.WriteHeader(http.StatusNotFound)
		return
	}

	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(cultureObject)
}

func findCultureByCoords(all []storage.Culture, lat float64, long float64) (storage.Culture, error) {
	lat = Truncate3precision(lat)
	long = Truncate3precision(long)
	for _, c := range all {
		reestrLat := Truncate3precision(c.Coordinate.Latitude)
		reestrLong := Truncate3precision(c.Coordinate.Longitude)

		if lat == reestrLat && long == reestrLong {
			return c, nil
		}
	}

	return storage.Culture{}, errors.New("culture object not found")
}

func Truncate3precision(num float64) float64 {
	return float64(int(num*1000)) / 1000
}
