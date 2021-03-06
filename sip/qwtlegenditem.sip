// The SIP interface definition for QwtLegendItem.
//
// Copyright (C) 2000 Mark Colclough
// Copyright (C) 2001-2004 Gerard Vermeulen
//
// This file is part of PyQwt.
//
// -- LICENSE --
//
// PyQwt is free software; you can redistribute it and/or modify it under the
// terms of the GNU General Public License as published by the Free Software
// Foundation; either version 2 of the License, or (at your option) any later
// version.
//
// PyQwt is distributed in the hope that it will be useful, but WITHOUT ANY
// WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
// FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
// details.
//
// You should have received a copy of the GNU General Public License along with
// PyQwt; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
// Suite 330, Boston, MA 02111-1307, USA.
//
// In addition, as a special exception, Gerard Vermeulen gives permission to
// link PyQwt dynamically with commercial, non-commercial or educational
// versions of Qt, PyQt and sip, and distribute PyQwt in this form, provided
// that equally powerful versions of Qt, PyQt and sip have been released under
// the terms of the GNU General Public License.
//
// If PyQwt is dynamically linked with commercial, non-commercial or
// educational versions of Qt, PyQt and sip, PyQwt becomes a free plug-in
// for a non-free program.
//
// -- LICENSE --


class QwtLegendItem
{
public:
%TypeHeaderCode
#include <qwt_legend.h>
%End
    enum IdentifierMode {
        NoIdentifier = 0,
        ShowLine = 1,
        ShowSymbol = 2,
        ShowText = 4,
    };

    QwtLegendItem();
    QwtLegendItem(const QwtSymbol &, const QPen &);

    virtual ~QwtLegendItem();

    void setIdentifierMode(int);
    int identifierMode() const;

    void setSymbol(const QwtSymbol &);
    const QwtSymbol& symbol() const;

    void setCurvePen(const QPen &);
    const QPen& curvePen() const;

    virtual void drawIdentifier(QPainter *, const QRect &) const;
    virtual void drawItem(QPainter *, const QRect &) const;

    virtual void setTitle(const QString &) = 0;
    virtual QString title() const = 0;

protected:
    virtual QwtText *titleText() const = 0;
    virtual void updateItem();
};

// Local Variables:
// mode: C++
// c-file-style: "stroustrup"
// End:
