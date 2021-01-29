package main

import (
	"errors"
	"fmt"
	"github.com/EatsLemons/Legacy/apps/backend/storage"
	"github.com/joho/godotenv"
	"os"
)

func main() {
	loadEnv()

	var s3Endpoint = os.Getenv("S3_STORAGE_ENDPOINT")
	var s3Access = os.Getenv("S3_STORAGE_ACCESS_KEY")
	var s3Secret = os.Getenv("S3_STORAGE_SECRET_KEY")

	downloader := storage.NewReestrDownloader(s3Endpoint, s3Access, s3Secret)

	var cultures = downloader.Download()

	fmt.Printf("%+v \n", cultures[120000].Data.General.Name)
}

func findCultureByCoords(all []storage.CultureObject, lat float64, long float64) (storage.CultureObject, error) {
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

	return storage.CultureObject{}, errors.New("culture object not found")
}

func loadEnv() {
	if err := godotenv.Load(".env"); err != nil {
		panic("No .env file found")
	}
}

func truncate3precision(num float64) float64 {
	return float64(int(num*1000)) / 1000
}
