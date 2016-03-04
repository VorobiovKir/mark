var MainController = function($http) {

    var that = this;

    this.isPreload = false;
    this.countPreload = 0;

    this.url = {
        server: 'http://127.0.0.1:8000/',
        dropbox: {
            getMetaFiles: 'dropbox/get_meta_files/',
            getNotesFast: 'dropbox/get_notes_final/',
            getNotesSlow: 'dropbox/get_notes_alt'
        },

        getFullPath: function(path) {
            return this.server + eval('this.' + path);
        }
    }

    this.user = {
        projects: '',
        tags: '',
        notes: {
            order: '',
            unorder: '',
            full_info_ord: ''
        }
    }

    this.filters = {
        projects: 'notebook',
        tags: 'tag'
    }

    this.preloading = function(count) {
        that.countPreload++;
        if (that.countPreload == count) {
            that.isPreload = true;
            $('#load-screen').css({
                'display': 'block'
            });
            $('body').css({
                'overflow': 'auto'
            });
        }
    }


    this.getMetaFiles = function(search_type) {
        var req = {
            method: 'GET',
            url: this.url.getFullPath('dropbox.getMetaFiles'),
            params: {
                'search_type': search_type
            }
        };

        $http(req).success(function(data) {
            (search_type == 'projects') ?
                that.user.projects = data['result'] : that.user.tags = data['result'];
                that.preloading(3);
        });
    }

    this.getNotes = function(mode) {
        var path = (mode == 'fast') ? 'dropbox.getNotesFast' : 'dropbox.getNotesSlow';
        $http.get(this.url.getFullPath(path)).success(function(data) {
            that.user.notes.full_info_ord = data['result'];
            that.preloading(3);
            // that.user.notes.order = data['format_result'];
            // console.log(that.user.notes.order);
        });
    }

    this.startPage = function() {
        that.getMetaFiles('tags');
        that.getMetaFiles('projects');
        that.getNotes('fast');
    }

    that.startPage();
}
