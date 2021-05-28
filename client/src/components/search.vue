<template>
  <div class="Search">

    <select name="province" id="province" class="Select" v-on:change="indexSelect01" v-model="indexId">
      <option :value="item.select" v-for="(item,index) in select01" class="options">{{item.name}}</option>  <!---->
    </select>
    <!--二级菜单-->
    <select name="city" id="city" class="Select" v-model="indexId2" >
      <option :value="k.select" v-for="k in select02" class="options">{{k.name}}</option>
    </select>

    <input
        placeholder="请输入并按下回车进行搜索(忽略大小写)"
        type="text"
        class="searchInput"
        v-model="searchStr"
        v-on:keyup.enter="search"
    />
    <h2 v-show="errorinfo">暂无数据，请重新输入</h2>
    <div v-if="indexId=== 'find'" class="container" v-show="retItems.length">
        <table>
            <thead>
            <tr>
                <th width="10%">用户名</th>
                <th width="15%">邮箱</th>
                <th width="10%">来源</th>
                <th width="10%">泄漏时间</th>
                <th width="20%">密码</th>
                <th width="35%">hash密码</th>
            </tr>
            </thead>
            <tbody>
                <tr v-for="item in retItems">
                    <td width="10%">{{ item.user }}</td>
                    <td width="15%">{{ item.email }}</td>
                    <td width="10%">{{ item.source }}</td>
                    <td width="10%">{{ item.xtime }}</td>
                    <td width="20%">{{ item.password }}</td>
                    <td width="35%">{{ item.passwordHash    }}</td>
                </tr>
            </tbody>
        </table>

        <div v-show="datacnts>10" class="pageselect">
            <select class="showpages" @change="changepages" v-model="selectedP">
                <option v-for="opt in pageoptions" v-bind:value="opt.value" class="options">
                    {{ opt.text }}
                </option>
            </select>
            <p>每页显示数据条数：
                <input
                    type="int"
                    class="limitInput"
                    v-model="limit"
                    v-on:keyup.enter="changepages"
                />
            </p>
        </div>
        <p v-model="datacnts">查询结果有 {{ datacnts }} 条数据</p>
    </div>
    <div v-else-if="indexId=== 'info'" class="container" v-show="retItems.length">
      <table>
        <thead>
        <tr>
          <th width="10%">身份证</th>
          <th width="15%">姓名</th>
          <th width="10%">性别</th>
          <th width="10%">地址</th>
          <th width="20%">QQ</th>
          <th width="20%">手机号</th>
          <th width="15%">微博uid</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="item in retItems">
          <td width="10%">{{ item.id }}</td>
          <td width="15%">{{ item.name }}</td>
          <td width="10%">{{ item.sex }}</td>
          <td width="10%">{{ item.address }}</td>
          <td width="20%">{{ item.qq }}</td>
          <td width="20%">{{ item.phonenumber }}</td>
          <td width="15%">{{ item.weibo_uid }}</td>
        </tr>
        </tbody>
      </table>

      <div v-show="datacnts>10" class="pageselect">
        <select class="showpages" @change="changepages" v-model="selectedP">
          <option v-for="opt in pageoptions" v-bind:value="opt.value" class="options">
            {{ opt.text }}
          </option>
        </select>
        <p>每页显示数据条数：
          <input
            type="int"
            class="limitInput"
            v-model="limit"
            v-on:keyup.enter="changepages"
          />
        </p>
      </div>
      <p v-model="datacnts">查询结果有 {{ datacnts }} 条数据</p>
    </div>
    <div v-else>
      查询错误
    </div>
  </div>
</template>

<script>
// 改为CDN引入
// import axios from 'axios'
export default {
  name: 'Search',
  data () {
    return {
      limit : 10,
      selectedP: 1,
      searchStr: '',
      pageStr: '',
      errorinfo: '',
      datacnts: 0,
      pageoptions: [],
      options: [
        { text: '用户名', value: 'user' },
        { text: '密码', value: 'password' },
        { text: '邮箱', value: 'email' },
        { text: '哈希密码', value: 'passwordHash' }
      ],
      retItems: [],
      analysisInfos: [],

      select01: [],//获取的一级数组数据
      select02: [],//获取的二级数组数据
      indexId:'账密',//定义分类一的默认值
      indexId2:'用户名',
      indexNum:0,//定义一级菜单的下标


    }
  },
  created() {
    axios.get('/get_selector')
      .then(response => {
        if(response.data.status === 'ok'){
          let mes = response.data;
          this.select01 = mes.data;
          console.log("省级")
          console.log(this.select01)
          this.indexSelect01();
        }
        else{
          this.errorinfo = '初始化级联数据错误';
        }
      })
      .catch(error => {
        console.log(error);
      });
  },

  methods:{

        search: function () {
            this.pageoptions = [];
            this.limit = 10;
            this.selectedP = 1;
            this.errorinfo = '';
            console.log(this.indexId)
            console.log(this.indexId2)

            // axios.get('/find/user/' + this.searchStr)
          // axios.get('/find/'+ this.indexId2 + '/' + this.searchStr)
          axios.get('/'+ this.indexId +  '/'+ this.indexId2 + '/' + this.searchStr)
                .then(response => {
                    if(response.data.status === 'ok'){
                        this.retItems = response.data.data.concat();
                        this.pageStr = this.searchStr;
                        this.searchStr = '';
                        this.datacnts = response.data.datacounts;
                        var n = 0;
                        while ( n < Math.ceil(this.datacnts/this.limit)) {
                            n = n + 1;
                            this.pageoptions.push({
                                text: '第 ' +  n + ' 页',
                                value: n
                            });
                        }
                    }
                    else{
                        this.retItems = [];
                        this.searchStr = [];
                        this.datacnts = 0;
                        this.errorinfo = '输入错误';
                    }
                })
                .catch(error => {
                    console.log(error);
                });
        },
        changepages: function() {
            axios.get('/'  + this.indexId + '/'+ this.indexId2 + '/' + this.pageStr + '?limit=' + this.limit + '&skip=' + this.limit * (this.selectedP-1))
                .then(response => {
                    if(response.data.status === 'ok'){
                        this.pageoptions = [];
                        var n = 0;
                        while ( n <  Math.ceil(this.datacnts/this.limit)) {
                            n = n + 1;
                            this.pageoptions.push({
                                text: '第 ' +  n + ' 页',
                                value: n
                            });
                        }
                        this.retItems = response.data.data.concat();
                        this.searchStr = '';
                        this.datacnts = response.data.datacounts;
                    }
                    else{
                        this.retItems = [];
                        this.searchStr = [];
                        this.datacnts = 0;
                        this.errorinfo = '输入错误';
                    }
                })
                .catch(error => {
                    console.log(error);
                });
        }
        ,
        indexSelect01(){
          let i = 0;
          for (i = 0;i<this.select01.length;i++) {
            if (this.select01[i].select == this.indexId){
              // if (this.select01[i].id == this.indexId){
              this.indexNum = i;
              break
            }
          }

          this.select02 = this.select01[this.indexNum].obj;
          console.log("市级数据")
          console.log(this.select02)
        }

    }
}
</script>

<style>

h1, h2 {
  font-weight: normal;
}

h1 {
  color: #fff;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

table{
    margin-top: 2em;
    border:1px solid ;
    padding: 20px;
    border-collapse: collapse;
    font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    font-size: 0.8em;
}

.container {
  text-align: center;
  overflow: hidden;
  width: 60em;
  margin: 0 auto;
}

.container table {
  width: 100%;
}

.container td {
    font-size: 10px;
}
.container td, .container th {
  font-size: 1.2em;
  overflow: auto;
  padding: 10px;
}

.container th {
  border-bottom: 1px solid #ddd;
  position: relative;
  width: 30px;
}
.searchInput {
    outline: none;
    height: 30px;
    width: 680px;
    border : 1px solid  #FFFFFF;
    padding : 15px 30px 15px 30px;
    font-size: 1em;
    font-family: BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
}
.searchInput:focus {
    box-shadow: 2px 2px 2px #336633;
}
.limitInput {
    outline: none;
    height: 15px;
    width: 20px;
    border : 1px solid  #FFFFFF;
    padding : 5px 5px 5px 5px;
    font-size: 1em;
    font-family: BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
}
.limitInput:focus {
    box-shadow: 2px 2px 2px #336633;
}
.Select {
    border : 1px solid  #FFFFFF;
    font-size: 1em;
    font-family: BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    outline: none;
    border: none;
    padding: 0 0 0 10px;
}
.Select .options {
    outline: none;
    border: none;
}
.Select {
    height: 62px;
    width: 100px;
}
.showpages {
    border : 1px solid  #FFFFFF;
    font-size: 1em;
    font-family: BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    outline: none;
    border: none;
    padding: 0 0 0 10px;
    position: relative;
    margin: 0 auto;
    margin-top: 1em;
}
.pageselect input{
}
</style>
