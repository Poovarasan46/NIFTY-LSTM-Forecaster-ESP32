#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>
#include <SPI.h>

// =====================================
// TFT PINS
// =====================================

#define TFT_CS     5
#define TFT_RST    4
#define TFT_DC     2

#define TFT_MOSI   23
#define TFT_SCLK   18

Adafruit_ST7735 tft =
    Adafruit_ST7735(
        TFT_CS,
        TFT_DC,
        TFT_RST
    );

// =====================================
// WIFI
// =====================================

const char* ssid =
    "YOUR_WIFI_NAME";

const char* password =
    "YOUR_WIFI_PASSWORD";

// =====================================
// FLASK SERVER
// =====================================

const char* serverURL =
    "http://YOUR_SERVER_IP:5000/predict";

// =====================================
// VARIABLES
// =====================================

float currentPrice = 0;
float predictedPrice = 0;

String trend = "N/A";

int confidence = 0;

float chartData[30];

// =====================================
// WIFI CONNECT
// =====================================

void connectWiFi()
{
    tft.fillScreen(ST77XX_BLACK);

    tft.setTextColor(ST77XX_WHITE);
    tft.setTextSize(1);

    tft.setCursor(5, 20);
    tft.println("Connecting WiFi...");

    WiFi.begin(
        ssid,
        password
    );

    while (
        WiFi.status() != WL_CONNECTED
    )
    {
        delay(500);
        Serial.print(".");
    }

    Serial.println();
    Serial.println("Connected!");

    tft.fillScreen(ST77XX_BLACK);

    tft.setCursor(10, 30);
    tft.println("WiFi Connected");

    delay(1000);
}

// =====================================
// MINI CHART
// =====================================

void drawMiniChart(
    float values[],
    int count
)
{
    int x0 = 5;
    int y0 = 115;

    int width = 118;
    int height = 40;

    float minV = values[0];
    float maxV = values[0];

    for(int i = 1; i < count; i++)
    {
        if(values[i] < minV)
            minV = values[i];

        if(values[i] > maxV)
            maxV = values[i];
    }

    if(maxV == minV)
        return;

    for(int i = 0; i < count - 1; i++)
    {
        int x1 =
            x0 +
            (i * width) /
            (count - 1);

        int x2 =
            x0 +
            ((i + 1) * width) /
            (count - 1);

        int y1 =
            y0 +
            height -
            ((values[i] - minV) *
            height /
            (maxV - minV));

        int y2 =
            y0 +
            height -
            ((values[i + 1] - minV) *
            height /
            (maxV - minV));

        tft.drawLine(
            x1,
            y1,
            x2,
            y2,
            ST77XX_CYAN
        );
    }
}

// =====================================
// GET DATA FROM API
// =====================================

bool getPrediction()
{
    if(
        WiFi.status() != WL_CONNECTED
    )
    {
        Serial.println(
            "WiFi Disconnected"
        );

        return false;
    }

    HTTPClient http;

    http.begin(serverURL);

    int httpCode =
        http.GET();

    if(httpCode <= 0)
    {
        Serial.print(
            "HTTP Error: "
        );

        Serial.println(httpCode);

        http.end();

        return false;
    }

    String payload =
        http.getString();

    Serial.println(payload);

    JsonDocument doc;

    DeserializationError error =
        deserializeJson(
            doc,
            payload
        );

    if(error)
    {
        Serial.println(
            "JSON Parse Error"
        );

        http.end();

        return false;
    }

    currentPrice =
        doc["current"];

    predictedPrice =
        doc["predicted"];

    trend =
        String(
            (const char*)
            doc["trend"]
        );

    confidence =
        doc["confidence"];

    JsonArray chart =
        doc["chart"];

    for(
        int i = 0;
        i < 30;
        i++
    )
    {
        chartData[i] =
            chart[i];
    }

    http.end();

    return true;
}

// =====================================
// DASHBOARD
// =====================================

void drawDashboard()
{
    tft.fillScreen(
        ST77XX_BLACK
    );

    // Title

    tft.setTextColor(
        ST77XX_YELLOW
    );

    tft.setTextSize(2);

    tft.setCursor(15, 5);

    tft.println("NIFTY");

    // Current

    tft.setTextColor(
        ST77XX_WHITE
    );

    tft.setTextSize(1);

    tft.setCursor(5, 35);
    tft.print("Current:");

    tft.setCursor(65, 35);
    tft.print(
        currentPrice,
        2
    );

    // Prediction

    tft.setCursor(5, 55);
    tft.print("Predict:");

    tft.setCursor(65, 55);
    tft.print(
        predictedPrice,
        2
    );

    // Trend

    tft.setCursor(5, 75);
    tft.print("Trend:");

    if(trend == "UP")
    {
        tft.setTextColor(
            ST77XX_GREEN
        );

        tft.setCursor(65, 75);
        tft.print("UP");

        // Up Arrow

        tft.drawLine(
            100,85,
            110,65,
            ST77XX_GREEN
        );

        tft.drawLine(
            110,65,
            120,85,
            ST77XX_GREEN
        );
    }
    else
    {
        tft.setTextColor(
            ST77XX_RED
        );

        tft.setCursor(65, 75);
        tft.print("DOWN");

        // Down Arrow

        tft.drawLine(
            100,65,
            110,85,
            ST77XX_RED
        );

        tft.drawLine(
            110,85,
            120,65,
            ST77XX_RED
        );
    }

    // Confidence

    tft.setTextColor(
        ST77XX_WHITE
    );

    tft.setCursor(5, 95);

    tft.print("Conf: ");

    tft.print(confidence);

    tft.print("%");

    // Mini Chart

    drawMiniChart(
        chartData,
        30
    );
}

// =====================================
// SETUP
// =====================================

void setup()
{
    Serial.begin(115200);

    SPI.begin(
        TFT_SCLK,
        -1,
        TFT_MOSI,
        -1
    );

    tft.initR(
        INITR_BLACKTAB
    );

    tft.setRotation(0);

    tft.fillScreen(
        ST77XX_BLACK
    );

    connectWiFi();

    if(
        getPrediction()
    )
    {
        drawDashboard();
    }
}

// =====================================
// LOOP
// =====================================

unsigned long lastUpdate = 0;

void loop()
{
    if(
        millis() -
        lastUpdate >
        300000
    )
    {
        lastUpdate =
            millis();

        if(
            getPrediction()
        )
        {
            drawDashboard();

            Serial.println(
                "Dashboard Updated"
            );
        }
    }
}
