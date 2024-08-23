#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>
#include <microhttpd.h>
#include <unistd.h>
#include <pthread.h>

#define PORT 8002

static char price_cache[256] = "Price not available yet.";

static size_t write_callback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t total_size = size * nmemb;
    // Simple parsing - to be replaced with actual HTML parsing
    char *price_start = strstr((char *)contents, "price");
    if (price_start) {
        sscanf(price_start, "price: %s", price_cache);
    }
    return total_size;
}

void scrape() {
    CURL *curl;
    CURLcode res;

    curl = curl_easy_init();
    if(curl) {
        curl_easy_setopt(curl, CURLOPT_URL, "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4");
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_perform(curl);
        curl_easy_cleanup(curl);
    }
}

static int answer_to_connection(void *cls, struct MHD_Connection *connection, const char *url,
                                const char *method, const char *version, const char *upload_data,
                                size_t *upload_data_size, void **con_cls) {
    const char *page = price_cache;
    struct MHD_Response *response;
    int ret;

    response = MHD_create_response_from_buffer(strlen(page), (void *)page, MHD_RESPMEM_PERSISTENT);
    ret = MHD_queue_response(connection, MHD_HTTP_OK, response);
    MHD_destroy_response(response);

    return ret;
}

void *scheduled_task(void *arg) {
    while (1) {
        scrape();
        sleep(6); // Sleep for 6 seconds
    }
    return NULL;
}

int main() {
    struct MHD_Daemon *daemon;
    pthread_t scraper_thread;

    daemon = MHD_start_daemon(MHD_USE_SELECT_INTERNALLY, PORT, NULL, NULL, &answer_to_connection, NULL, MHD_OPTION_END);
    if (NULL == daemon) return 1;

    pthread_create(&scraper_thread, NULL, scheduled_task, NULL);
    pthread_join(scraper_thread, NULL);

    MHD_stop_daemon(daemon);

    return 0;
}
