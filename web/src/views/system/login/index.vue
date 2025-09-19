<template>
	<div class="login-container flex">
		<!-- 左侧logo区域 -->
		<div class="login-left">
			<div class="login-left-logo">
				<img :src="siteLogo" />
				<div class="login-left-logo-text">
					<!-- 直接设置标题内容为"知识库管理系统" -->
      				<span class="main-title">知识库管理系统</span>
				</div>
			</div>
		</div>
		
		<!-- 登录页面背景图 -->
		<div v-if="loginBg" class="login-bg-container">
			<img :src="loginBg" class="loginBg" />
		</div>
		
		<!-- 右侧背景图层定位方式 -->
		<div class="login-right-bg"></div>
		
		<!-- 右侧输入框定位方式 -->
		<div class="login-right flex">
			<div class="login-right-warp">
				<div class="login-right-warp-mian">
					<div class="login-right-warp-main-title">
						{{userInfos.pwd_change_count===0?'初次登录修改密码':'账号登录'}}
					</div>
					<div class="login-right-warp-main-form">
						<div v-if="!state.isScan">
							<el-tabs v-model="state.tabsActiveName" >
                <el-tab-pane :label="$t('message.label.changePwd')" name="changePwd"  v-if="userInfos.pwd_change_count===0">
                  <ChangePwd />
                </el-tab-pane>
								<el-tab-pane :label="$t('message.label.one1')" name="account" v-else>
									<Account />
								</el-tab-pane>
							</el-tabs>
						</div>
            <OAuth2 />
					</div>
				</div>
			</div>
		</div>

		<!-- <div class="login-authorization">
			<p>Copyright © {{ getSystemConfig['login.copyright'] || '2021-2025 django-vue-admin.com' }} 版权所有</p>
			<p class="la-other" style="margin-top: 5px;">
				<a href="https://beian.miit.gov.cn" target="_blank">{{ getSystemConfig['login.keep_record'] ||
					'晋ICP备18005113号-3' }}</a>
				|
				<a :href="getSystemConfig['login.help_url'] ? getSystemConfig['login.help_url'] : '#'"
					target="_blank">帮助</a>
				|
				<a
					:href="getSystemConfig['login.privacy_url'] ? getBaseURL(getSystemConfig['login.privacy_url']) : '#'">隐私</a>
				|
				<a
					:href="getSystemConfig['login.clause_url'] ? getBaseURL(getSystemConfig['login.clause_url']) : '#'">条款</a>
			</p>
		</div> -->
	</div>
</template>

<script setup lang="ts" name="loginIndex">
import {defineAsyncComponent, onMounted, reactive, computed, watch} from 'vue';
import { storeToRefs } from 'pinia';
import { useThemeConfig } from '/@/stores/themeConfig';
import { NextLoading } from '/@/utils/loading';
import logoMini from '/@/assets/logo-1.png';
import loginBg from '/@/assets/login-bg.png';
import { SystemConfigStore } from '/@/stores/systemConfig'
import { getBaseURL } from "/@/utils/baseUrl";

// 引入组件
const Account = defineAsyncComponent(() => import('/@/views/system/login/component/account.vue'));
const ChangePwd = defineAsyncComponent(() => import('/@/views/system/login/component/changePwd.vue'));
const OAuth2 = defineAsyncComponent(() => import('/@/views/system/login/component/oauth2.vue'));

import _ from "lodash-es";
import {useUserInfo} from "/@/stores/userInfo";
const { userInfos } = storeToRefs(useUserInfo());

// 定义变量内容
const storesThemeConfig = useThemeConfig();
const { themeConfig } = storeToRefs(storesThemeConfig);
const state = reactive({
	tabsActiveName: 'account',
	isScan: false,
});

watch(()=>userInfos.value.pwd_change_count,(val)=>{
  if(val===0){
    state.tabsActiveName ='changePwd'
  }else{
    state.tabsActiveName ='account'
  }
},{deep:true,immediate:true})

// 获取布局配置信息
const getThemeConfig = computed(() => {
	return themeConfig.value;
});

const systemConfigStore = SystemConfigStore()
const { systemConfig } = storeToRefs(systemConfigStore)
const getSystemConfig = computed(() => {
	return systemConfig.value
})

const siteLogo = computed(() => {
	if (!_.isEmpty(getSystemConfig.value['login.site_logo'])) {
		return getSystemConfig.value['login.site_logo']
	}
	return logoMini
});

// 页面加载时
onMounted(() => {
	NextLoading.done();
});
</script>

<style scoped lang="scss">
.login-container {
	//width: 1920px;
	//height: 1080px;
	height: 100%;
	background: var(--el-color-white);
	position: relative;
	z-index: 1;

	.login-left {
		flex: 1;
		position: relative;
		// background-color: rgba(211, 239, 255, 1);
		margin-right: 100px;
		z-index: 3;

		.login-left-logo {
			display: flex;
			align-items: center;
			position: absolute;
			top: 40px;
			left: 80px;
			z-index: 4;
			animation: logoAnimation 0.3s ease;

			img {
				width: 40px;
				height: 46px;
			}

			.login-left-logo-text {
                margin: 0;
                padding: 0;
                
                .main-title {
                    width: 259px;
                    height: 34px;
					position: relative;
  					left: 13px;
                    font-family: "AlimamaShuHeiTi";
                    font-weight: bold;
                    font-size: 36px;
                    color: #333333;
                    opacity: 1;
                    letter-spacing: 40;
                    line-height: 32px;
                    text-align: left;
                    display: inline-block;
                    overflow: visible;
                    white-space: nowrap;
                }
            }
		}
	}

	// 登录背景图容器
	.login-bg-container {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		z-index: 0;
		overflow: hidden;
		
		.loginBg {
			width: 100%;
			height: 100%;
			object-fit: cover;
		}
	}

	// 右侧背景图层样式调整
	.login-right-bg {
		position: absolute;
		top: 0;
		right: 0;
		width: 720px;
		height: 100%;
		background-color: #FFFFFF;
		opacity: 0.6;
		z-index: 2;
	}

	.login-right {
		width: 720px;
		height: 1080px;
		position: relative;
		z-index: 3;

		.login-right-warp {
			width: 720px;
			height: 1080px;
			position: relative;
			overflow: hidden;
			z-index: 4;

			.login-right-warp-mian {
				width: 100%; /* 继承父容器宽度 */
				height: 100%; /* 继承父容器高度（1080px） */
				position: relative; /* 关键：作为子元素的定位基准 */
				
				::v-deep .el-tabs__header {
					display: none !important;  /* 强制隐藏头部 */
				}
				.login-right-warp-main-title {
					position: absolute; /* 基于父容器定位 */
					top: 213px;
					left: 282px;
					width: 156px;
					height: 38px;
					font-family: Microsoft YaHei;
					font-weight: bold;
					font-size: 38px;
					color: #333333;
					line-height: 32px;
				}

				.login-right-warp-main-form {
					width: 100%; /* 继承父容器宽度 */
					height: 100%; /* 继承父容器高度 */
					padding: 0; /* 保持内边距为0 */
					position: relative;
					z-index: 5;
					/* 可选：如果需要内容垂直居中，可添加如下flex布局 */
					// display: flex;
					// flex-direction: column;
					// justify-content: center; /* 垂直居中 */
					// align-items: center; /* 水平居中 */
				}
			}
		}
	}

	.login-authorization {
		position: absolute;
		bottom: 30px;
		left: 0;
		right: 0;
		text-align: center;
		z-index: 3;

		p {
			font-size: 14px;
			color: rgba(0, 0, 0, 0.5);
		}

		a {
			color: var(--el-color-primary);
			margin: 0 5px;
		}
	}
}

// 动画定义
@keyframes logoAnimation {
	0% {
		transform: scale(0.8);
		opacity: 0;
	}
	100% {
		transform: scale(1);
		opacity: 1;
	}
}

// 响应式调整
@media screen and (max-width: 1600px) {
	.login-container {
		.login-left {
			margin-right: 50px;
			
			.login-left-logo {
				left: 40px;
			}
		}
		
		.login-right {
			width: 600px;
			
			.login-right-warp {
				width: 450px;
			}
		}
		
		.login-right-bg {
			width: 600px;
		}
	}
}

@media screen and (max-width: 1400px) {
	.login-container {
		.login-right {
			width: 500px;
			
			.login-right-warp {
				width: 400px;
				height: 450px;
			}
		}
		
		.login-right-bg {
			width: 500px;
		}
	}
}
</style>