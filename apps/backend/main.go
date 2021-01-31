package main

import (
	"fmt"
	"github.com/EatsLemons/Legacy/apps/backend/api"
	"github.com/EatsLemons/Legacy/apps/backend/storage"
	"github.com/joho/godotenv"
	"net/http"
	"os"
)

var cultures []storage.CultureObject

func main() {
	loadEnv()

	var s3Endpoint = os.Getenv("S3_STORAGE_ENDPOINT")
	var s3Access = os.Getenv("S3_STORAGE_ACCESS_KEY")
	var s3Secret = os.Getenv("S3_STORAGE_SECRET_KEY")

	downloader := storage.NewReestrDownloader(s3Endpoint, s3Access, s3Secret)

	fmt.Print("loading culture objects...")

	cultures = downloader.Download()

	fmt.Print("loading complete")

	http.HandleFunc("/v1/find", func(w http.ResponseWriter, req *http.Request) {
		api.FindByCoords(cultures, w, req)
	})

	fmt.Print("http listen on :8080")
	http.ListenAndServe(":8080", nil)
}

func loadEnv() {
	if err := godotenv.Load(".env"); err != nil {
		panic("No .env file found")
	}
}
