// qwt_numarray.h: encapsulates all of PyQwt's calls to the numarray C-API.
// 
// Copyright (C) 2001-2003 Gerard Vermeulen
// Copyright (C) 2000 Mark Colclough
//
// This file is part of PyQwt
//
// PyQwt is free software; you can redistribute it and/or modify it under the
// terms of the GNU General Public License as published by the Free Software
// Foundation; either version 2 of the License, or (at your option) any later
// version.
//
// PyQwt is distributed in the hope that it will be useful, but WITHOUT ANY
// WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
// FOR A PARTICULAR PURPOSE.  See the GNU  General Public License for more
// details.
//
// You should have received a copy of the GNU General Public License along with
// PyQwt; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
// Suite 330, Boston, MA 02111-1307, USA.
//
// In addition, as a special exception, Gerard Vermeulen gives permission to
// link PyQwt with commercial, non-commercial and educational versions of Qt,
// PyQt and sip, and distribute PyQwt in this form, provided that equally
// powerful versions of Qt, PyQt and sip have been released under the terms
// of the GNU General Public License.
//
// If PyQwt is linked with commercial, non-commercial and educational versions
// of Qt, PyQt and sip, Python scripts using PyQwt do not have to be released
// under the terms of the GNU General Public License. 
//
// You must obey the GNU General Public License in all respects for all of the
// code used other than Qt, PyQt and sip, including the Python scripts that are
// part of PyQwt.


#ifndef QWT_NUMARRAY_H
#define QWT_NUMARRAY_H

#include <Python.h>
#include <qimage.h>
#include <qwt_array.h>

#ifdef HAS_NUMARRAY
// numarray's C-API pointer
extern void **PyQwt_Numarray_PyArray_API;
// hides numarray's import_array()
void import_NumarrayArray();
// returns 1, 0, -1 in case of success, wrong PyObject type, failure
int try_NumarrayArray_to_QwtArray(PyObject *in, QwtArray<double> &out);
int try_NumarrayArray_to_QImage(PyObject *in, QImage &out);
#endif // HAS_NUMARRAY

#endif // QWT_NUMARRAY

// Local Variables:
// mode: C++
// c-file-style: "stroustrup"
// End:
