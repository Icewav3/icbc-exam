package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/joho/godotenv"
)

const (
	loginURL        = "https://onlinebusiness.icbc.com/deas-api/v1/webLogin/webLogin"
	appointmentsURL = "https://onlinebusiness.icbc.com/deas-api/v1/web/getAvailableAppointments"
)

type loginBody struct {
	LastName      string `json:"drvrLastName"`
	LicenceNumber string `json:"licenceNumber"`
	Keyword       string `json:"keyword,omitempty"`
}

func mustEnv(key string) string {
	v := os.Getenv(key)
	if v == "" {
		log.Fatalf("missing env %s", key)
	}
	return v
}

func login() string {
	body := loginBody{
		LastName:      mustEnv("ICBC_LASTNAME"),
		LicenceNumber: mustEnv("ICBC_LICENCENUMBER"),
		Keyword:       mustEnv("ICBC_KEYWORD"),
	}
	jsonBytes, _ := json.Marshal(body)

	req, _ := http.NewRequest(http.MethodPut, loginURL, bytes.NewBuffer(jsonBytes))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		log.Fatal(err)
	}
	defer resp.Body.Close()

	if resp.StatusCode == 200 {
		return resp.Header.Get("Authorization")
	}
	return ""
}

func main() {
	_ = godotenv.Load()

	token := login()
	if token == "" {
		log.Fatal("auth failed")
	}
	fmt.Println("Auth OK, token:", token[:10], "…")
	// TODO: call appointmentsURL
}
