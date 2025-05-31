<template>
  <a-layout id="app-layout" class="app-container">
    <a-layout-header class="app-header">
      <div class="header-left">
        <div class="logo">
          <img src="/logo-dark.png" height="40px" alt="logo">
        </div>
        <a-menu mode="horizontal" :default-selected-keys="['1']" class="app-menu">
          <a-menu-item key="1" class="menu-item">
            <a-icon type="form"/>
            <span>标题摘要生成</span>
            <router-link to='/summary_generate'></router-link>
          </a-menu-item>

          <a-menu-item key="2" class="menu-item">
            <a-icon type="login"/>
            <span>批量生成</span>
            <router-link to='/batch_generate'></router-link>
          </a-menu-item>

          <a-menu-item key="3" class="menu-item">
            <a-icon type="clock-circle"/>
            <span>处理记录</span>
            <router-link to='/history_list'></router-link>
          </a-menu-item>

          <a-menu-item key="4" class="menu-item" v-if="userinfo && userinfo['isAdmin']==1">
            <a-icon type="setting"/>
            <span>管理后台</span>
            <a-badge :count="statistics.unverify" class="admin-badge"/>
            <router-link to='/verify'></router-link>
          </a-menu-item>
        </a-menu>
      </div>

      <!-- 登录框 -->
      <div v-if="!isLogin" class="login-container">
        <a-form-model layout="inline" :model="formInline" @submit="handleLogin" @submit.native.prevent class="login-form">
          <a-form-model-item>
            <a-input v-model="formInline.email" placeholder="E-Mail" class="login-input">
              <a-icon slot="prefix" type="user" class="input-icon"/>
            </a-input>
          </a-form-model-item>
          <a-form-model-item>
            <a-input v-model="formInline.password" type="password" placeholder="密码" class="login-input">
              <a-icon slot="prefix" type="lock" class="input-icon"/>
            </a-input>
          </a-form-model-item>
          <a-form-model-item>
            <a-button type="primary" html-type="submit" class="login-button" :disabled="formInline.user === '' || formInline.password === ''">
              登录
            </a-button>
            <a-button class="register-button" @click="showModal">
              注册
            </a-button>
          </a-form-model-item>
        </a-form-model>

        <a-modal
            title="注册用户"
            :visible="modal.visible"
            @ok="handleModalCancel"
            @cancel="handleModalCancel"
            class="register-modal"
        >
          <user-register></user-register>
        </a-modal>
      </div>

      <!-- 已登录显示 -->
      <div v-if="isLogin" class="user-info">
        <a-avatar icon="user" class="user-avatar"/>
        <span class="username">{{ userinfo.username }}</span>
        <a-button class="logout-button" @click="handleLogout">
          退出
        </a-button>
      </div>
    </a-layout-header>

    <a-layout-content class="app-content">
      <a-breadcrumb class="app-breadcrumb">
        <a-breadcrumb-item></a-breadcrumb-item>
      </a-breadcrumb>
      <div class="content-container">
        <router-view></router-view>
      </div>
    </a-layout-content>

    <a-layout-footer class="app-footer">
      ©2025 智文研发组 <br>版权所有
    </a-layout-footer>
  </a-layout>
</template>

<script>
import axios from "axios";
import UserRegister from "@/components/UserRegister";

export default {
  components: {UserRegister},
  data() {
    return {
      collapsed: false,
      formInline: {
        email: '',
        password: '',
      },
      isLogin: false,
      userinfo: undefined,

      statistics: {
        unverify: 0
      },

      modal: {
        visible: false,
        confirmLoading: false
      },
    };
  },
  beforeCreate() {
    this.HOST = process.env.VUE_APP_SERVER_URL;
  },
  mounted() {
    this.checkLogin();
    this.getStatus();

  },
  methods: {
    handleLogin() {
      let formData = new FormData();
      formData.append('email', this.formInline.email);
      formData.append('password', this.formInline.password);
      this.isLogin = true;

      axios.post(this.HOST + "/api/user_login", formData, {
        headers: {
          "Content-Type": "multipart/form-data"
        }
      }).then(
          res => {
            let code = res.data['code'];
            let msg = res.data['msg'];

            if (code == 0) {
              this.$message.success('欢迎您：' + res.data['body']['userinfo']['username']);
              window.localStorage.setItem('userinfo', JSON.stringify(res.data['body']['userinfo']));
              window.localStorage.setItem('token', res.data['body']['token']);

              window.location.reload();

            } else {
              this.$message.error('错误信息：' + msg);
            }

          }
      ).catch(error => {
            this.$message.error('网络错误：' + error);

          }
      )
    },
    handleLogout() {
      window.localStorage.clear();
      this.isLogin = false;
      this.$message.success('退出成功！');
    },
    checkLogin() {
      //检查登录态
      let userinfo = window.localStorage.getItem('userinfo');
      if (userinfo) {
        this.isLogin = true;
        this.userinfo = JSON.parse(window.localStorage.getItem('userinfo'));
      } else {
        this.$notification.open({
          message: '当前未登录',
          description:
              '未登录时，您仍可以用游客身份浏览，但无法使用生成、管理等功能。',
          icon: <a-icon type="smile" style="color: #108ee9"/>,
        });
      }
    },
    getStatus() {
      axios.get(this.HOST + "/api/status", {}).then(
          res => {
            console.log(res.data);
            this.statistics.unverify = res.data['body']['today_unverify'];

          }
      )

    },
    showModal() {
      this.modal.visible = true;
    },
    handleModalCancel(){
      this.modal.visible = false;
    }
  },

};
</script>

<style scoped>
.app-container {
  min-height: 100vh;
}

.app-header {
  background: #fff;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0,21,41,.08);
  position: fixed;
  width: 100%;
  z-index: 1000;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  margin-right: 40px;
  display: flex;
  align-items: center;
}

.app-menu {
  background: transparent;
  border-bottom: none;
  line-height: 64px;
}

.menu-item {
  margin: 0 4px;
  padding: 0 16px;
  height: 64px;
  line-height: 64px;
  color: rgba(0,0,0,.85);
  font-size: 14px;
}

.menu-item:hover {
  color: #1890ff !important;
  background: rgba(24,144,255,.1) !important;
}

.menu-item.ant-menu-item-selected {
  color: #1890ff !important;
  background: rgba(24,144,255,.1) !important;
}

.admin-badge {
  margin-left: 8px;
}

.login-container {
  display: flex;
  align-items: center;
}

.login-form {
  display: flex;
  align-items: center;
}

.login-input {
  width: 200px;
  margin-right: 16px;
}

.input-icon {
  color: rgba(0,0,0,.25);
}

.login-button {
  margin-right: 8px;
  height: 32px;
  padding: 0 15px;
  font-size: 14px;
  border-radius: 4px;
  background: #1890ff;
  border-color: #1890ff;
}

.login-button:hover {
  background: #40a9ff;
  border-color: #40a9ff;
}

.register-button {
  height: 32px;
  padding: 0 15px;
  font-size: 14px;
  border-radius: 4px;
  color: #1890ff;
  border-color: #1890ff;
}

.register-button:hover {
  color: #40a9ff;
  border-color: #40a9ff;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 0 24px;
}

.user-avatar {
  margin-right: 8px;
  background: #1890ff;
}

.username {
  margin-right: 16px;
  color: rgba(0,0,0,.85);
  font-size: 14px;
}

.logout-button {
  height: 32px;
  padding: 0 15px;
  font-size: 14px;
  border-radius: 4px;
  color: #1890ff;
  border-color: #1890ff;
}

.logout-button:hover {
  color: #40a9ff;
  border-color: #40a9ff;
}

.app-content {
  margin-top: 64px;
  padding: 24px;
  background: #f0f2f5;
  min-height: calc(100vh - 64px - 70px);
}

.app-breadcrumb {
  margin: 16px 0;
}

.content-container {
  background: #fff;
  padding: 24px;
  min-height: 360px;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}

.app-footer {
  text-align: center;
  padding: 16px 50px;
  color: rgba(0,0,0,.45);
  font-size: 14px;
  background: #f0f2f5;
}

/* 响应式调整 */
@media screen and (max-width: 768px) {
  .app-header {
    padding: 0 12px;
  }

  .header-left {
    flex-direction: column;
    align-items: flex-start;
  }

  .logo {
    margin-right: 0;
    margin-bottom: 8px;
  }

  .app-menu {
    width: 100%;
  }

  .menu-item {
    padding: 0 8px;
  }

  .login-form {
    flex-direction: column;
  }
  
  .login-input {
    width: 100%;
    margin-right: 0;
    margin-bottom: 8px;
  }
  
  .user-info {
    padding: 0 12px;
  }
  
  .app-content {
    margin: 64px 8px 0;
    padding: 12px;
  }
  
  .content-container {
    padding: 12px;
  }
}
</style>
