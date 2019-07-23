#include <gst/gst.h>
#include <string>
#include <iostream>
#include "redirect_source.h"

static gboolean bus_callback(GstBus* bus, GstMessage* message, gpointer data);
static GstElement* pipeline;

int start_redirect(std::string source_ip, int source_port, 
		   std::string dest_ip, int dest_port) {
    std::string p1("tcpclientsrc host=");
    std::string p2(" port=");
    std::string p3(" ! gdpdepay ! rtph264depay ! rtph264pay ! gdppay ! tcpserversink host=");
    std::string p4(" port=");
    std::string p5(" sync=false");
    std::string descr = p1 + source_ip + p2 + std::to_string(source_port) + p3 + dest_ip + p4 + std::to_string(dest_port) + p5;
    std::cout << "Redirection pipeline:\n    " << descr << std::endl;
    
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

    gst_element_set_state(GST_ELEMENT(pipeline), GST_STATE_PLAYING);
    return 0;
}

int stop_redirect() {
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
