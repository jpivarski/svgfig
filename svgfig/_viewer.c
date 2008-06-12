// plothon/svg/viewer.c is a part of Plothon.
// Copyright (C) 2007 Jim Pivarski <jpivarski@gmail.com>
// 
// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
// 
// Full licence is in the file COPYING and at http://www.gnu.org/copyleft/gpl.html

#include <Python.h>
#include <gtk/gtk.h>
#include <gdk/gdkdrawable.h>
#include <gdk/gdkcairo.h>
#include <librsvg-2/librsvg/rsvg.h>
#include <librsvg-2/librsvg/rsvg-cairo.h>

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif

static GtkWidget *window;
static GtkWidget *drawing_area;
static char ready = 0;
static char done = 1;
static RsvgHandle *rsvg = NULL;

static void draw(GtkWidget *widget, cairo_t *cr) {
  if (rsvg == NULL) return;

  double window_width, window_height;
  window_width = widget->allocation.width;
  window_height = widget->allocation.height;

  RsvgDimensionData dimensions;
  rsvg_handle_get_dimensions(rsvg, &dimensions);
  unsigned int w, h;
  w = dimensions.width;
  h = dimensions.height;
  double aspect_ratio;
  aspect_ratio = 1.0 * w / h;

  double page_width, page_height;
  page_height = window_height - 8;
  page_width = page_height * aspect_ratio;
  if (page_width > window_width - 8) {
    page_width = window_width - 8;
    page_height = page_width / aspect_ratio;
  }
  double x = (window_width - page_width + 4.) / 2.;
  double y = (window_height - page_height + 4.) / 2.;

  cairo_rectangle(cr, x, y, page_width, page_height);
  cairo_set_source_rgb(cr, 1, 1, 1);
  cairo_fill(cr);

  cairo_translate(cr, x, y);
  cairo_scale(cr, page_width/w, page_height/h);
  rsvg_handle_render_cairo(rsvg, cr);
}

static gboolean expose_event(GtkWidget *widget, GdkEventExpose *event) {
  ready = 0;

  cairo_t *cr;
  cr = gdk_cairo_create(widget->window);
  cairo_rectangle(cr, event->area.x, event->area.y, event->area.width, event->area.height);
  cairo_clip(cr);
  draw(widget, cr);
  cairo_destroy(cr);

  ready = 1;
  return FALSE;
}

static void *thread() {
  done = 0;

  gtk_init(0, NULL);
  window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
  gtk_window_set_title(GTK_WINDOW(window), "SVGFig");
  drawing_area = gtk_drawing_area_new();
  gtk_container_add(GTK_CONTAINER(window), drawing_area);

  g_signal_connect(GTK_OBJECT(window), "delete_event", (GtkSignalFunc)(gtk_main_quit), NULL);
  g_signal_connect(GTK_OBJECT(drawing_area), "expose_event", (GtkSignalFunc)(expose_event), NULL);
  gtk_widget_set_events(drawing_area, GDK_EXPOSURE_MASK);
  
  gtk_widget_show(drawing_area);
  gtk_widget_show(window);

  ready = 1;
  gtk_main();
  done = 1;
  return NULL;
}

static PyObject *_viewer_str(PyObject *self, PyObject *args) {
  char *str_source = NULL;
  int str_size;
  if (!PyArg_ParseTuple(args, "es#", "utf-16", &str_source, &str_size)) {
    PyErr_SetString(PyExc_TypeError, "source must be an SVG string or Unicode object.");
    return NULL;
  }

  if (done) {
    GError *error = NULL;
    if (!g_thread_create(thread, NULL, FALSE, &error)) {
      PyErr_Format(PyExc_RuntimeError, "Could not create GDK thread: %s", error->message);
      PyMem_Free(str_source);
      return NULL;
    }
  }

  if (rsvg != NULL) {
    g_object_unref(rsvg);
    rsvg = NULL;
  }

  GError* error = NULL;
  rsvg = rsvg_handle_new_from_data((guint8*)(str_source), (gsize)(str_size), &error);
  if (rsvg == NULL) {
    PyErr_Format(PyExc_RuntimeError, "Couldn't parse SVG: %s", error->message);
    PyMem_Free(str_source);
    return NULL;
  }

  g_thread_yield();
  while (!ready);

  gdk_threads_enter();
  gtk_widget_queue_draw(drawing_area);
  gdk_threads_leave();

  PyMem_Free(str_source);
  return Py_BuildValue("O", Py_None);
}

static PyMethodDef _viewer_methods[] = {
  {"str", ((PyCFunction)(_viewer_str)), METH_VARARGS, ""},
  {NULL}
};

PyMODINIT_FUNC init_viewer() {
  Py_InitModule3("_viewer", _viewer_methods, "");
  rsvg_init();
  g_thread_init(NULL);
  gdk_threads_init();
}
