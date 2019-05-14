$(function () {
    var categories = [];
    var templates = [];
    var taskflows = [];
    $.ajax({
        url: site_url + "template/get_business_basic_info/" + BIZ_CC_ID + "/",
        type: 'GET',
        dataType: 'json',
        async: false,
        success: function(req){
            categories = req.task_categories;
        },
        error: function(response){
            alert_msg(gettext("获取业务信息失败，请稍后重试！"), 4);
        }
    });

    //获取用户模板信息
    $.ajax({
        url: SITE_URL + "api/v3/template/?business__cc_id="+ BIZ_CC_ID,
        type: 'GET',
        dataType: 'json',
        async: false,
        success: function (req) {
            templates = req.objects;
        },
        error: function(response){
            alert_msg(response.status_code, 4);
        }
    });

    //获取业务任务数据
    $.ajax({
        url: SITE_URL + "api/v3/taskflow/?limit=3&business__cc_id="+ BIZ_CC_ID,
        type: 'GET',
        dataType: 'json',
        async: false,
        success: function (req) {
            taskflows = req.objects;
        },
        error: function(response){
            alert_msg(response.status_code, 4);
        }
    });

    Vue.directive('scrollbar', {
        twoWay: true, // 双向绑定
        params: [],
        bind: function () {
            var self = this;
            $(this.el).mCustomScrollbar();
        }
    });

    //快速创建任务和模板收藏
    var fast_template = new Vue({
        el: "#index_collection_box",
        data: {
            templates: templates,
            category: [],
            keepBoxShow: false,
            tooLong: false,
            add_data_tip:true
        },
        methods: {
            init_category: function(){
                for (var i = 0; i < this.templates.length; i++) {
                    this.category.push({"value": this.templates[i].category_name});
                }
                this.category = unique(this.category);
            },
            toKeep: function (index) {
                this.add_data_tip=false;
                var keepLen = 0;
                for (var i = 0; i < this.templates.length; i++) {
                    if (this.templates[i].is_add) {
                        keepLen++;
                    }
                }
                if (keepLen >= 10) {
                    this.tooLong = true;
                    if (this.templates[index].is_add) {
                        this.templates[index].is_add = 0;
                        this.tooLong = false;
                    }
                } else {
                    this.templates[index].is_add ? this.templates[index].is_add = 0 : this.templates[index].is_add = 1;
                    //ajax后台保存数据
                    param = {
                        'method': 'add',
                        'template_id': this.templates[index].template_id
                    };
                    $.ajax({
                        url: SITE_URL + 'template/api/collect/' + BIZ_CC_ID + '/',
                        type: 'POST',
                        dataType: 'json',
                        data: param,
                        success: function (req) {
                        },
                        error: function(response){
                            alert_msg(response.status_code, 4);
                        }
                    })
                }

            },
            noKeep: function (index) {
                this.add_data_tip=true;
                this.templates[index].is_add ? this.templates[index].is_add = 0 : this.templates[index].is_add = 1;
                param = {
                    'method': 'remove',
                    'template_id': this.templates[index].template_id
                };
                $.ajax({
                    url: SITE_URL + 'template/api/collect/' + BIZ_CC_ID + '/',
                    type: 'POST',
                    dataType: 'json',
                    data: param,
                    success: function (req) {
                    },
                    error: function(response){
                        alert_msg(response.status_code, 4);
                    }
                })
            },
            showKeepBox: function () {
                this.keepBoxShow = true;
            },
            hideKeepBox: function () {
                this.keepBoxShow = false;
            }
        },
        ready: function(){
            this.init_category();
        }
    });

    var statistics_view = new Vue({
        el: '#index-list',
        data:{
            templates: templates,
            categories: categories,
            template_cate:[],
            template_count: 0,
            taskflow_cate: [],
            taskflow_count: 0,
            appmaker_cate:[],
            appmaker_count: 0
        },
        methods:{
            get_init_count_cate: function(){
                var self = this;
                var count_cate = {};
                for(var i = 0; i < self.categories.length; i++){
                    count_cate[self.categories[i]['value']] = 0;
                }
                return count_cate;
            },
            get_taskflow_cate: function(){
                var self = this;
                $.ajax({
                    url: SITE_URL + 'taskflow/api/query_task_count/' + BIZ_CC_ID + '/',
                    type: 'POST',
                    dataType: 'json',
                    data: {
                        'group_by': 'status',
                    },
                    success: function(req){
                        if(!req.result){
                            alert_msg(req.message, 4);
                            self.taskflow_count = 0;
                            self.taskflow_cate = [];
                            return
                        }
                        self.taskflow_count = req.data.total;
                        for(var i=0; i<req.data.groups.length; i++){
                            self.taskflow_cate.push([req.data.groups[i].name, req.data.groups[i].value]);
                        }
                    },
                    error: function(response){
                        alert_msg(response.status_code, 4);
                    }
                })
            },
             get_template_cate: function(){
                var self = this;
                self.template_count = self.templates.length;
                var count_cate = self.get_init_count_cate();
                for(var i = 0; i < self.templates.length; i++) {
                    count_cate[self.templates[i].category] += 1;
                }
                for(var i = 0; i < self.categories.length; i++){
                    self.template_cate.push([self.categories[i]['name'], count_cate[self.categories[i]['value']]]);
                }
            },
            get_appmaker_cate: function(){
                var self = this;
                $.ajax({
                    url: SITE_URL + 'api/v3/appmaker/?business__cc_id='+ BIZ_CC_ID,
                    type: 'GET',
                    dataType: 'json',
                    success: function(req){
                        self.appmaker_count = req.objects.length;
                        var count_cate = self.get_init_count_cate();
                        for(var i = 0; i < req.objects.length; i++) {
                            count_cate[req.objects[i].category] += 1;
                        }
                        for(var i = 0; i < self.categories.length; i++){
                            self.appmaker_cate.push([self.categories[i]['name'], count_cate[self.categories[i]['value']]]);
                        }
                    },
                    error: function(response){
                        alert_msg(response.status_code, 4);
                    }
                })
            }
        },
        ready:function(){
            this.get_taskflow_cate();
            this.get_template_cate();
            this.get_appmaker_cate();
        }
    });

    function update_news(buisness_news, index, status){
        var now = new Date();
        var task_info = buisness_news[index];
        if(status == 'FINISHED'){
            var finish_time = new Date(Date.parse(task_info.finish_time));
            var start_time = new Date(Date.parse(task_info.start_time));
            task_info.status_fa = "fa fa-check check";
            task_info.status_title = gettext("任务已完成");
            task_info.show_time = task_info.finish_time;
        }else if(status == 'RUNNING' || status == 'BLOCKED'){
            var finish_time = now;
            var start_time = new Date(Date.parse(task_info.start_time));
            task_info.status_fa = "fa fa-spinner fa-spin";
            task_info.status_title = gettext("任务执行中");
            task_info.show_time = task_info.start_time;
        }else if(status == 'FAILED'){
            var finish_time = now;
            var start_time = new Date(Date.parse(task_info.start_time));
            task_info.status_fa = "fa fa-warning hulue";
            task_info.status_title = gettext("任务执行失败");
            task_info.show_time = task_info.start_time;
        }else if(status == 'SUSPENDED'){
            var finish_time = now;
            start_time = new Date(Date.parse(task_info.start_time));
            task_info.status_fa = "fa fa-pause stop";
            task_info.status_title = gettext("任务暂停中");
            task_info.show_time = task_info.start_time;
        }else if(status == 'REVOKED'){
            var finish_time = new Date(Date.parse(task_info.finish_time));
            var start_time = new Date(Date.parse(task_info.start_time));
            task_info.status_fa = "fa fa-check check";
            task_info.status_title = gettext("任务已撤销");
            task_info.show_time = task_info.finish_time;
        }else{
            var finish_time = now;
            var start_time = now;
            task_info.status_fa = "fa fa-clock-o";
            task_info.status_title = gettext("任务未执行");
            task_info.show_time = task_info.create_time;
            task_info.action = gettext("创建了一个");
        }
        task_info.time_consuming = cal_time_consuming(start_time, finish_time);
        task_info.oldTime = cal_time_snapshot(start_time, now);
    }

    var business_news = new Vue({
        el: '#index-news',
        data: {
            business_news: [],
            is_news: true,
            is_info: false,
        },
        methods: {
            get_business_news: function () {
                var self = this;
                self.business_news = taskflows.slice(0, 3)
                for (var i = 0; i < self.business_news.length; i++) {
                    var task_info = self.business_news[i];
                    self.business_news[i].url = SITE_URL + 'taskflow/execute/' + BIZ_CC_ID + '/?instance_id=' + task_info.id;
                    self.business_news[i].action = gettext("执行了一个");
                    $.ajax({
                        url: SITE_URL + 'taskflow/api/status/' + BIZ_CC_ID + '/',
                        method: "GET",
                        data: {'instance_id': task_info.id},
                        async: false,
                        success: function (resp) {
                            if (resp.result) {
                                update_news(self.business_news, i, resp.data.state);
                            } else {
                                console.error(resp.message, 4);
                            }
                        },
                        error: function (resp) {
                            console.error(resp);
                        }
                    });
                }
                if (self.business_news.length == 0) {
                    self.is_news = false;
                    self.is_info = true;
                }
                $(".seLeft").mCustomScrollbar({
                    setHeight: 484, //设置高度
                    theme: "minimal-dark" //设置风格
                });
                console.log(self.business_news)
            }
        },
        ready: function () {
            this.get_business_news();
        }
    });

    //设置任务类型占比
    $.ajax({
        url: SITE_URL + 'taskflow/api/query_task_count/' + BIZ_CC_ID + '/',
        type: 'POST',
        dataType: 'json',
        data: {
            'group_by': 'category',
        },
        success: function(req){
            if(!req.result){
                alert_msg(req.message, 4);
                self.taskflow_count = 0;
                self.taskflow_cate = [];
                return
            }
            var total = req.data.total;
            if(total === 0){
                create_scene_rate([{'name': gettext('暂无相关数据'), 'value': 1.0}])
            }else{
                create_scene_rate(req.data.groups);
            }
        },
        error: function(response){
            alert_msg(response.status_code, 4);
        }
    })
});

/* 数组去重 */
function unique(a) {
    var res = [];
    for (var i = 0, len = a.length; i < len; i++) {
        var item = a[i];
        for (var j = 0, jLen = res.length; j < jLen; j++) {
            if (res[j].value === item.value)
                break;
        }
        if (j === jLen)
            res.push(item);
    }
    return res;
}

function cal_time_snapshot(date1, date2) {
    var time_diata = date2.getTime() - date1.getTime();
    var result = '';
    if (time_diata == 0) {
        result = ''
    } else if (time_diata < 60 * 1000) {
        result = gettext("刚刚")
    } else if (time_diata < 60 * 60 * 1000) {
        result = Math.floor(time_diata / (60 * 1000)) + gettext('分前')
    } else if (time_diata < 24 * 3600 * 1000) {
        result = Math.floor(time_diata / (3600 * 1000)) + gettext('小时前')
    } else if (time_diata < 7 * 24 * 3600 * 1000) {
        result = Math.floor(time_diata / (24 * 3600 * 1000)) + gettext('天前')
    } else {
        result = date1.toLocaleDateString()
    }
    return result
}

function cal_time_consuming(date1, date2) {
    var time_diata = date2.getTime() - date1.getTime();
    if (time_diata == 0) {
        result = '--'
    } else if (time_diata < 60 * 1000) {
        result = Math.floor(time_diata / 1000) + gettext('秒')
    } else if (time_diata < 60 * 60 * 1000) {
        result = Math.floor(time_diata / (60 * 1000)) + gettext('分')
    } else if (time_diata < 24 * 3600 * 1000) {
        result = Math.floor(time_diata / (3600 * 1000)) + gettext('小时')
    } else {
        result = Math.floor(time_diata / (24 * 3600 * 1000)) + gettext('天')
    }
    return result
}


//创建图表
function create_scene_rate(data) {
    var myChart = echarts.init(document.getElementById('main'));
    var option = {
        title: {
            text: gettext('任务类型占比'),
            x: 'left'
        },
        tooltip: {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        legend: {
            show: false,
            data: []
        },
        series: [
            {
                name: gettext('任务类型占比'),
                type: 'pie',
                radius: '55%',
                center: ['50%', '55%'],
                hoverAnimation: true,
                selectedOffset: 20,
                data: data,
            }
        ],
        itemStyle: {
            emphasis: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0,0,0,1)'
            }
        },
        //color:['#8DBFF4','#5CA3ED','#7CC1FF','#A3CCF7','#B9D8F9','#5CA3ED','#71B0F1', '#4A9BFF']
        color: ["#0073c2", "#0085e0", "#1893e7", "#4ba6e5", "#62b3eb", "#7cc1ff", "#add1f8", "#5ca3ed", "#b9d8f9", "#71b0f1"]
    };
    myChart.setOption(option);
}
