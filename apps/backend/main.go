package main

import (
	"errors"
	"flag"
	"fmt"
	"github.com/EatsLemons/Legacy/apps/backend/storage"
)

var s3Endpoint = flag.String("s3endpoint", "s3endpoint", "S3 endpoint")
var s3Access = flag.String("s3access", "s3access", "Access key to S3")
var s3Secret = flag.String("s3secret", "s3secret", "Secret key to S3")

func main() {
	flag.Parse()

	downloader := storage.NewReestrDownloader(*s3Endpoint, *s3Access, *s3Secret)

	var cultures = downloader.Download()

	fmt.Printf("%+v \n", cultures[120000].Data.General.Name)
}

func findCultureByCoords(all []storage.CultureObject, lat float64, long float64) (storage.CultureObject, error) {
	lat = Truncate3precision(lat)
	long = Truncate3precision(long)
	for _, c := range all {
		if len(c.Data.General.Address.MapPosition.Coordinates) < 2 {
			continue
		}

		reestrLat := Truncate3precision(c.Data.General.Address.MapPosition.Coordinates[0])
		reestrLong := Truncate3precision(c.Data.General.Address.MapPosition.Coordinates[1])

		if lat == reestrLat && long == reestrLong {
			return c, nil
		}
	}

	return storage.CultureObject{}, errors.New("culture object not found")
}

func Truncate3precision(num float64) float64 {
	return float64(int(num*1000)) / 1000
}
