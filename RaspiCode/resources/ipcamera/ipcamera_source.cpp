#include <gst/gst.h>
#include <string>
#include "ipcamera_source.h"

static gboolean bus_callback(GstBus* bus, GstMessage* message, gpointer data);
static GstElement* pipeline;

int initialise(std::string ip, int port) {
    gst_init(NULL, NULL);
    std::string port_str = std::to_string(port);
    std::string p1("v4l2src ! omxh264enc ! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=");
    std::string p2(" port=");
    std::string p3(" sync=false");
    std::string descr = p1 + ip + p2 + port_str + p3;
    
    GError* error = NULL;
    pipeline = gst_parse_launch(descr.c_str(), &error);
    
    if (error) {
	g_print("Could not construct pipeline: %s\n", error->message);
	g_error_free(error);
	return -1;
    }
    
    GstBus* bus = gst_element_get_bus(pipeline);
    gst_bus_add_watch(bus, bus_callback, nullptr);
    gst_object_unref(bus);
    return 0;
}

int start_stream() {
    gst_element_set_state(GST_ELEMENT(pipeline), GST_STATE_PLAYING);
    return 0;
}

int stop_stream() {
    gst_element_set_state(GST_ELEMENT(pipeline), GST_STATE_PAUSED);
    return 0;
}

int cleanup() {
    gst_element_set_state(GST_ELEMENT(pipeline), GST_STATE_NULL);
    gst_object_unref(GST_OBJECT(pipeline));
    return 0;
}


static gboolean bus_callback(GstBus* bus, GstMessage* message, gpointer data) {
    switch(GST_MESSAGE_TYPE(message)) {
    case GST_MESSAGE_ERROR: {
	GError* err;
	gchar* debug;
	
	gst_message_parse_error(message, &err, &debug);
	g_print("Error: %s\n", err->message);
	g_error_free(err);
	g_free(debug);
	break;
    }
    case GST_MESSAGE_EOS:
	g_print("End of stream\n");
	break;
    default:
	break;
    }
    return TRUE;
}
