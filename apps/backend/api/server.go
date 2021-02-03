package api

import (
	"encoding/json"
	"errors"
	"github.com/EatsLemons/Legacy/apps/backend/storage"
	"net/http"
	"strconv"
)

func FindByCoords(all []storage.RosReestrCulture, w http.ResponseWriter, req *http.Request) {
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

func findCultureByCoords(all []storage.RosReestrCulture, lat float64, long float64) (storage.RosReestrCulture, error) {
	lat = Truncate3precision(lat)
	long = Truncate3precision(long)
	for _, c := range all {
		if len(c.Data.General.Address.MapPosition.Coordinates) < 2 {
			continue
		}

		reestrLat := Truncate3precision(c.Data.General.Address.MapPosition.Coordinates[1])
		reestrLong := Truncate3precision(c.Data.General.Address.MapPosition.Coordinates[0])

		if lat == reestrLat && long == reestrLong {
			return c, nil
		}
	}

	return storage.RosReestrCulture{}, errors.New("culture object not found")
}

func Truncate3precision(num float64) float64 {
	return float64(int(num*1000)) / 1000
}
