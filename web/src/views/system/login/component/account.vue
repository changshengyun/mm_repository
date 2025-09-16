<template>
	<el-form ref="formRef" size="large" class="login-content-form" :model="state.ruleForm" :rules="rules" @keyup.enter="loginClick">
		<el-form-item class="login-animation1" prop="username">
			<el-input type="text" :placeholder="'请输入账号'" v-model="ruleForm.username"
				clearable autocomplete="off">
				<template #prefix>
					<img 
						src="/src/assets/account-1.png" 
						class="custom-account-icon" 
						alt="用户图标"
					>
				</template>
			</el-input>
		</el-form-item>
		<el-form-item class="login-animation2" prop="password">
			<el-input :type="isShowPassword ? 'text' : 'password'" :placeholder="'请输入密码'"
				v-model="ruleForm.password">
				<template #prefix>
					<img 
						src="/src/assets/key-1.png" 
						class="custom-account-icon" 
						alt="用户图标"
					>
				</template>
				<!-- <template #suffix>
					<i class="iconfont el-input__icon login-content-password"
						:class="isShowPassword ? 'icon-yincangmima' : 'icon-xianshimima'"
						@click="isShowPassword = !isShowPassword">
					</i>
				</template> -->
			</el-input>
		</el-form-item>
		<el-form-item class="login-animation3" v-if="isShowCaptcha" prop="captcha">
			<el-col :span="15">
				<el-input type="text" maxlength="4" :placeholder="'请输入验证码'"
					v-model="ruleForm.captcha" clearable autocomplete="off">
					<template #prefix>
						<img 
						src="/src/assets/pwd-1.png" 
						class="custom-account-icon" 
						alt="用户图标"
					>
					</template>
				</el-input>
			</el-col>
			<el-col :span="1"></el-col>
			<el-col :span="8">
				<el-button class="login-content-captcha">
					<el-image :src="ruleForm.captchaImgBase" @click="refreshCaptcha" />
				</el-button>
			</el-col>
		</el-form-item>
		<el-form-item class="login-animation4">
			<el-button type="primary" class="login-content-submit" round @click="loginClick"
				:loading="loading.signIn">
				<span>登录</span>
			</el-button>
		</el-form-item>
		<el-form-item class="login-animation6">
			<el-col :span="10" class="text-center">
				<a href="/forgot-password" class="link-text">忘记密码</a>
			</el-col>
			<el-col :span="4" class="text-center separator">|</el-col>
			<el-col :span="10" class="text-center">
				<a href="/register" class="link-text">注册账号</a>
			</el-col>
		</el-form-item>
		<!-- 新增隐私协议复选框 -->
		<el-form-item class="login-animation5" prop="agreement" style="margin-top: 20px;">
			<el-checkbox v-model="ruleForm.agreement" class="agreement-checkbox">
				我已阅读并同意
				<a href="/privacy" target="_blank" class="privacy-link">《用户隐私协议》</a>
			</el-checkbox>
		</el-form-item>

	</el-form>
  <!--      申请试用-->
  <div style="text-align: center" v-if="showApply()">
    <el-button class="login-content-apply" link type="primary" plain round @click="applyBtnClick">
      <span>申请试用</span>
    </el-button>
  </div>
</template>

<script lang="ts">
import { toRefs, reactive, defineComponent, computed, onMounted, onUnmounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, FormInstance, FormRules } from 'element-plus';
import { useI18n } from 'vue-i18n';
import Cookies from 'js-cookie';
import { storeToRefs } from 'pinia';
import { useThemeConfig } from '/@/stores/themeConfig';
import { initFrontEndControlRoutes } from '/@/router/frontEnd';
import { initBackEndControlRoutes } from '/@/router/backEnd';
import { Session } from '/@/utils/storage';
import { formatAxis } from '/@/utils/formatTime';
import { NextLoading } from '/@/utils/loading';
import * as loginApi from '/@/views/system/login/api';
import { useUserInfo } from '/@/stores/userInfo';
import { DictionaryStore } from '/@/stores/dictionary';
import { SystemConfigStore } from '/@/stores/systemConfig';
import { BtnPermissionStore } from '/@/plugin/permission/store.permission';
import { Md5 } from 'ts-md5';
import { errorMessage } from '/@/utils/message';
import {getBaseURL} from "/@/utils/baseUrl";

export default defineComponent({
	name: 'loginAccount',
	setup() {
		const { t } = useI18n();
		const storesThemeConfig = useThemeConfig();
		const { themeConfig } = storeToRefs(storesThemeConfig);
		const { userInfos } = storeToRefs(useUserInfo());
		const route = useRoute();
		const router = useRouter();
		const state = reactive({
			isShowPassword: false,
			ruleForm: {
				username: '',
				password: '',
				captcha: '',
				captchaKey: '',
				captchaImgBase: '',
				agreement: false,
			},
			loading: {
				signIn: false,
			},
		});
		const rules = reactive<FormRules>({
			username: [
				{ required: true, message: '请输入账号', trigger: 'blur' },
			],
			password: [
				{
					required: true,
					message: '请输入密码',
					trigger: 'blur',
				},
			],
			captcha: [
				{
					required: true,
					message: '请输入验证码',
					trigger: 'blur',
				},
			],
			agreement: [
				{ 
					validator: (rule, value, callback) => {
						if (!value) {
							return callback(new Error('请阅读并同意《用户隐私协议》'));
						}
						callback();
					},
					trigger: 'change'
				}
			],
		})
		const formRef = ref();
		// 时间获取
		const currentTime = computed(() => {
			return formatAxis(new Date());
		});
		// 是否关闭验证码
		const isShowCaptcha = computed(() => {
			return SystemConfigStore().systemConfig['base.captcha_state'];
		});

		const getCaptcha = async () => {
			loginApi.getCaptcha().then((ret: any) => {
				state.ruleForm.captchaImgBase = ret.data.image_base;
				state.ruleForm.captchaKey = ret.data.key;
			});
		};
		const applyBtnClick = async () => {
			window.open(getBaseURL('/api/system/apply_for_trial/'));
		};
    const refreshCaptcha = async () => {
			state.ruleForm.captcha=''
			loginApi.getCaptcha().then((ret: any) => {
				state.ruleForm.captchaImgBase = ret.data.image_base;
				state.ruleForm.captchaKey = ret.data.key;
			});
		};
		const loginClick = async () => {
			if (!formRef.value) return
			await formRef.value.validate((valid: any) => {
				if (valid) {
					loginApi.login({ ...state.ruleForm, password: Md5.hashStr(state.ruleForm.password) }).then((res: any) => {
						if (res.code === 2000) {
              const {data} = res
              Cookies.set('username', res.data.username);
              Session.set('token', res.data.access);
              useUserInfo().setPwdChangeCount(data.pwd_change_count)
              if(data.pwd_change_count==0){
                return router.push('/login');
              }
							if (!themeConfig.value.isRequestRoutes) {
								// 前端控制路由，2、请注意执行顺序
								initFrontEndControlRoutes();
								loginSuccess();
							} else {
								// 模拟后端控制路由，isRequestRoutes 为 true，则开启后端控制路由
								// 添加完动态路由，再进行 router 跳转，否则可能报错 No match found for location with path "/"
								initBackEndControlRoutes();
								// 执行完 initBackEndControlRoutes，再执行 signInSuccess
								loginSuccess();
							}
						}
					}).catch((err: any) => {
						// 登录错误之后，刷新验证码
						refreshCaptcha();
					});
				} else {
					errorMessage("请填写登录信息")
				}
			})

		};



		// 登录成功后的跳转
		const loginSuccess = () => {
			//获取所有字典
			DictionaryStore().getSystemDictionarys();
			// 初始化登录成功时间问候语
			let currentTimeInfo = currentTime.value;
			// 登录成功，跳到转首页
      const pwd_change_count = userInfos.value.pwd_change_count
      if(pwd_change_count>0){
        // 如果是复制粘贴的路径，非首页/登录页，那么登录成功后重定向到对应的路径中
        if (route.query?.redirect) {
        	router.push({
        		path: <string>route.query?.redirect,
        		query: Object.keys(<string>route.query?.params).length > 0 ? JSON.parse(<string>route.query?.params) : '',
        	});
        } else {
        	router.push('/');
        }
        // 登录成功提示
        // 关闭 loading
        state.loading.signIn = true;
        const signInText = t('message.signInText');
        ElMessage.success(`${currentTimeInfo}，${signInText}`);
      }
			// 添加 loading，防止第一次进入界面时出现短暂空白
			NextLoading.start();
		};
		onMounted(() => {
			getCaptcha();
			//获取系统配置
			SystemConfigStore().getSystemConfigs();
		});
    // 是否显示申请试用按钮
    const showApply = () => {
      return window.location.href.indexOf('public') != -1
    }

		return {
			refreshCaptcha,
			loginClick,
			loginSuccess,
			isShowCaptcha,
			state,
			formRef,
			rules,
      applyBtnClick,
      showApply,
			...toRefs(state),
		};
	},
});
</script>

<style scoped lang="scss">
.login-content-form {
	/* 固定宽高并继承父容器定位 */
	width: 720px;
	height: 1080px;
	margin: 0;
	padding: 0;
	position: relative; /* 继承父容器的定位方式 */
	box-sizing: border-box; /* 确保宽高包含内边距和边框 */
	/* 动画效果保留 */
	@for $i from 1 through 4 {
		.login-animation#{$i} {
		  opacity: 0;
		  animation-name: error-num;
		  animation-duration: 0.5s;
		  animation-fill-mode: forwards;
		  animation-delay: calc($i/10) + s;
		}
	}	

	/* 用户名输入框 - 相对容器内部定位 */
	.login-animation1 {
		position: absolute;
		top: 317px;
		left: 93px;
		width: 535px;
		height: 87px;
		box-sizing: border-box;
		border-radius: 5px;
		background: #ffffff;
		border: 1px solid #5474D6;
		// 移除不必要的 background-clip（白色背景下无意义）
		
		// 穿透修改内部输入框容器
		::v-deep .el-input {
			width: 100%;
			height: 100%;
		}
		// 调整输入框高度、内边距及文本样式
		::v-deep .el-input__inner {
			height: 100%;
			// 文本样式
			width: 93px; /* 文本宽度 */
			height: 19px; /* 文本高度 */
			font-family: "Microsoft YaHei", sans-serif; /* 字体 */
			font-weight: 400; /* 字重 */
			font-size: 18px; /* 字号 */
			color: #999999; /* 文本颜色 */
			line-height: 32px; /* 行高 */
		}
		// 调整前缀图标大小（用户图标）
		::v-deep .custom-account-icon {
			width: 17px;  // 图标宽度
			height: 19px; // 图标高度
			margin-left: 18px;
			margin-right: 17px;
			margin-top: 34px;
			margin-bottom: 34px;
		}
		// /* 覆盖输入框验证错误时的边框样式（取消红色边框） */
		// ::v-deep .el-form-item.is-error .el-input__inner {
		// 	border-color: #00ff08 !important; /* 与正常状态边框颜色一致 */
		// 	box-shadow: none !important; /* 清除错误状态可能出现的阴影 */
		// }

	// 	/* 可选：如果需要隐藏错误提示文字 */
	// 	::v-deep .el-form-item__error {
	// 		display: none !important;
	// 	}
	}

	/* 密码输入框 */
	.login-animation2 {
		position: absolute;
		top: 442px;		
		left: 93px;
		width: 535px;
		height: 87px;		
		box-sizing: border-box;
		border-radius: 5px;
		background: #ffffff;
		border: 1px solid #5474D6;
		// 移除不必要的 background-clip（白色背景下无意义）
		
		// 穿透修改内部输入框容器
		::v-deep .el-input {
			width: 100%;
			height: 100%;
		}
		// 调整输入框高度、内边距及文本样式
		::v-deep .el-input__inner {
			height: 100%;
			// 文本样式
			width: 93px; /* 文本宽度 */
			height: 19px; /* 文本高度 */
			font-family: "Microsoft YaHei", sans-serif; /* 字体 */
			font-weight: 400; /* 字重 */
			font-size: 18px; /* 字号 */
			color: #999999; /* 文本颜色 */
			line-height: 32px; /* 行高 */
		}
		// 调整前缀图标大小（用户图标）
		::v-deep .custom-account-icon {
			width: 17px;  // 图标宽度
			height: 19px; // 图标高度
			margin-left: 18px;
			margin-right: 17px;
			margin-top: 34px;
			margin-bottom: 34px;
		}
	}

	/* 验证码区域 */
	.login-animation3 {
		position: absolute;
		top: 566px;
		left: 93px;
		width: 535px;
		height: 87px;
		box-sizing: border-box;	
		border-radius: 5px;
		background: #ffffff;
		border: 1px solid #5474D6;
		// 移除不必要的 background-clip（白色背景下无意义）
		
		// 穿透修改内部输入框容器
		::v-deep .el-input {
			width: 100%;
			height: 100%;
		}
		// 调整输入框高度、内边距及文本样式
		::v-deep .el-input__inner {
			height: 100%;
			// 文本样式
			width: 93px; /* 文本宽度 */
			height: 19px; /* 文本高度 */
			font-family: "Microsoft YaHei", sans-serif; /* 字体 */
			font-weight: 400; /* 字重 */
			font-size: 18px; /* 字号 */
			color: #999999; /* 文本颜色 */
			line-height: 32px; /* 行高 */
		}
		// 调整前缀图标大小（用户图标）
		::v-deep .custom-account-icon {
			width: 19px;  // 图标宽度
			height: 19px; // 图标高度
			margin-left: 17px;
			margin-right: 17px;
			margin-top: 33px;
			margin-bottom: 33px;
		}
		/* 调整验证码按钮容器（去除默认样式，避免干扰） */
		::v-deep .login-content-captcha {
			width: 100%;  // 按钮宽度占满列宽
			height: 100%;  // 按钮高度占满列高
			padding: 0;  // 清除按钮默认内边距
			border: none;  // 清除按钮边框
			background: transparent;  // 透明背景
		}
		::v-deep .login-content-captcha .el-image {
			width: 148px;
			height: 51px;
			margin-right:12px; 
			margin-top: 17px;
			margin-bottom: 17px;
		}
	}	
	/* 隐私协议 */
	.login-animation5 {
		animation-delay: 0.4s; /* 延迟时间比验证码项稍晚 */
		position: absolute;
		top: 650px;
		left: 95px;
		/* 调整复选框大小 */
		::v-deep.agreement-checkbox.el-checkbox__inner {
		/* 调整复选框尺寸（默认约14px） */
			width: 14px;
			height: 14px;
		}

		/* 复选框选中状态样式 */
		::v-deep .agreement-checkbox.is-checked .el-checkbox__inner {
			background-color: #5474D6; /* 选中后背景色 */
			border-color: #5474D6; /* 选中后边框色 */
		}

		::v-deep .agreement-checkbox .el-checkbox__label {
			/* 文本与复选框的间距（默认约8px） */
			padding-left: 5px; 
			font-size: 15px; /* 匹配文本高度15px */
			width: 212px; /* 匹配文本宽度212px */
			line-height: 15px; /* 行高与文本高度一致，确保垂直对齐 */
			color: #333333; 
		}
		// ::v-deep .agreement-checkbox.is-checked .el-checkbox__label {
		// 	color: #333333; /* 选中后文本颜色 */
		// }

		// 添加链接样式
		.privacy-link {
		color: #5474D6; /* 蓝色 */
		// text-decoration: underline;
		}
		.privacy-link:hover {
		color: #5474D6; /*  hover 深色 */
		}
	}

	// /* 登录按钮 */
	// .login-animation4 {
	//   position: absolute;
	//   top: 778px; 
	//   left: 93px;
	//   width: 535px;
	//   padding: 0 0px;
	//   box-sizing: border-box;
	//   background: #5474D6;
	//   border-radius: 10px;
	// }
	/* 登录按钮 */
	.login-animation4 {
		position: absolute;
		top: 778px; 
		left: 93px;
		width: 555px;
		padding: 0 10px;
		box-sizing: border-box;
		margin-top: 0; /* 确保无额外顶部间距 */
		font-family: "Microsoft YaHei", sans-serif; /* 字体 */
		/* 调整按钮大小、圆角和背景色 */
		::v-deep .login-content-submit {
			width: 535px; /* 宽度535px（继承父容器宽度） */
			height: 87px; /* 高度87px */
			font-family: "Microsoft YaHei", sans-serif; /* 字体设置为MicrosoftYaHei */
        	font-size: 90px; /* 字号调整为22px */
			border-radius: 10px; /* 圆角10px */
			background-color: #5474D6 !important; /* 填充颜色 */
			border: none !important; /* 去除边框 */
			color: #fff !important; /* 字体颜色（白色更清晰） */
			font-size: 18px; /* 可根据需要调整字号 */
			letter-spacing: 2px;
			font-weight: 800;
			margin-top: 0; /* 清除原有顶部间距 */
			display: flex; /* 确保文字居中 */
			align-items: center;
			justify-content: center;
		}

		/* 去除Element默认按钮的hover/active样式干扰 */
		::v-deep .login-content-submit:hover,
		::v-deep .login-content-submit:focus,
		::v-deep .login-content-submit:active {
			background-color: #5474D6 !important; /* 保持颜色不变 */
			box-shadow: none !important; /* 去除点击阴影 */
		}

	}
	// 忘记密码和注册账号区域
	.login-animation6 {
	position: absolute;
	top: 891px; 
	left: 280px;
	width: 160px;
	// 1. 取消固定高度限制，避免内容被截断
	height: auto; 
	// 2. 移除不必要的高度限制后，通过padding控制整体垂直范围
	padding: 5px 0; 
	box-sizing: border-box;
	opacity: 0;
	animation-name: error-num;
	animation-duration: 0.5s;
	animation-fill-mode: forwards;
	animation-delay: 0.45s;

	::v-deep .el-col {
		// 3. 子元素高度自适应，不强制100%（避免继承固定高度）
		height: auto; 
		display: flex;
		align-items: center;
		justify-content: center;
		// 4. 统一子元素行高基准
		line-height: 1; 
	}

	.link-text {
		// 5. 文字宽度自适应，避免超出父容器导致挤压分隔符
		width: auto; 
		// 6. 文字行高与字号匹配（16px字号对应16px行高）
		line-height: 16px; 
		height: 16px; // 固定文字高度，与行高一致
		font-family: Microsoft YaHei;
		font-weight: 400;
		font-size: 16px;
		color: #333333;
		text-align: center;
		&:hover {
		color: #4060c0;
		}
	}

	.separator {
		color: #333333;
		// 7. 分隔符字号微调（例如14px，根据需求调整）
		font-size: 14px; 
		// 8. 分隔符行高与自身字号匹配，确保垂直居中
		line-height: 14px; 
		height: 14px; // 固定分隔符高度，与行高一致
		// 9. 去除多余的align-items（父级已设置flex居中）
	}

	// 移除未使用的.line样式（代码中未用到）
	}



	/* 其他样式保持不变 */
	.login-content-password {
	  display: inline-block;
	  width: 20px;
	  cursor: pointer;	
	  &:hover {
	    color: #ffffff;
	  }
	}	
	.login-content-captcha {
	  width: 100%;
	  padding: 0;
	  font-weight: bold;
	  letter-spacing: 5px;
	}	
	.login-content-submit {
	  width: 100%;
	  letter-spacing: 2px;
	  font-weight: 800;
	  margin-top: 15px;
	}
}

// /* 补充动画关键帧（确保元素可见） */
// @keyframes error-num {
//   from {
//     opacity: 0;
//     transform: translateY(10px);
//   }
//   to {
//     opacity: 1;
//     transform: translateY(0);
//   }
// }
</style>
