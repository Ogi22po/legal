//
// psj/static/psj.js
//
// Copyright (C) 2011-19 Tomáš Pecina <tomas@pecina.cz>
//
// This file is part of legal.pecina.cz, a web-based toolbox for lawyers.
//
// This application is free software: you can redistribute it and/or
// modify it under the terms of the GNU General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This application is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//

'use strict';

function courtchanged(event) {

    $('#id_courtroom option').slice(1).remove();
    $('#id_judge option').slice(1).remove();

    var court = $(event.target).val();

    if (court) {
	$.get('/psj/court/' + court + '/', null, function(response) {
	    $('#id_courtroom option')
		.after($(response).filter('#courtroom').children());
	    $('#id_courtroom option:first').s(true);
	    $('#id_judge option')
		.after($(response).filter('#judge').children());
	    $('#id_judge option:first').s(true);
	});
    }
}

$(function() {
    $('#id_court').change(courtchanged);
});
