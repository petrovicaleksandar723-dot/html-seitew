"use strict";(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[181],{1057:function(e,t,r){r.d(t,{j:function(){return u}});var n=r(1119),i=r(2265),o=r(1448),a=r(1113);let s={uniforms:{tDiffuse:{value:null},h:{value:1/512}},vertexShader:`
      varying vec2 vUv;

      void main() {

        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );

      }
  `,fragmentShader:`
    uniform sampler2D tDiffuse;
    uniform float h;

    varying vec2 vUv;

    void main() {

    	vec4 sum = vec4( 0.0 );

    	sum += texture2D( tDiffuse, vec2( vUv.x - 4.0 * h, vUv.y ) ) * 0.051;
    	sum += texture2D( tDiffuse, vec2( vUv.x - 3.0 * h, vUv.y ) ) * 0.0918;
    	sum += texture2D( tDiffuse, vec2( vUv.x - 2.0 * h, vUv.y ) ) * 0.12245;
    	sum += texture2D( tDiffuse, vec2( vUv.x - 1.0 * h, vUv.y ) ) * 0.1531;
    	sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y ) ) * 0.1633;
    	sum += texture2D( tDiffuse, vec2( vUv.x + 1.0 * h, vUv.y ) ) * 0.1531;
    	sum += texture2D( tDiffuse, vec2( vUv.x + 2.0 * h, vUv.y ) ) * 0.12245;
    	sum += texture2D( tDiffuse, vec2( vUv.x + 3.0 * h, vUv.y ) ) * 0.0918;
    	sum += texture2D( tDiffuse, vec2( vUv.x + 4.0 * h, vUv.y ) ) * 0.051;

    	gl_FragColor = sum;

    }
  `},l={uniforms:{tDiffuse:{value:null},v:{value:1/512}},vertexShader:`
    varying vec2 vUv;

    void main() {

      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );

    }
  `,fragmentShader:`

  uniform sampler2D tDiffuse;
  uniform float v;

  varying vec2 vUv;

  void main() {

    vec4 sum = vec4( 0.0 );

    sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y - 4.0 * v ) ) * 0.051;
    sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y - 3.0 * v ) ) * 0.0918;
    sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y - 2.0 * v ) ) * 0.12245;
    sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y - 1.0 * v ) ) * 0.1531;
    sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y ) ) * 0.1633;
    sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y + 1.0 * v ) ) * 0.1531;
    sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y + 2.0 * v ) ) * 0.12245;
    sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y + 3.0 * v ) ) * 0.0918;
    sum += texture2D( tDiffuse, vec2( vUv.x, vUv.y + 4.0 * v ) ) * 0.051;

    gl_FragColor = sum;

  }
  `},u=i.forwardRef(({scale:e=10,frames:t=1/0,opacity:r=1,width:u=1,height:c=1,blur:f=1,near:d=0,far:v=10,resolution:m=512,smooth:h=!0,color:p="#000000",depthWrite:x=!1,renderOrder:g,...y},M)=>{let w,b;let D=i.useRef(null),E=(0,a.A)(e=>e.scene),P=(0,a.A)(e=>e.gl),R=i.useRef(null);u*=Array.isArray(e)?e[0]:e||1,c*=Array.isArray(e)?e[1]:e||1;let[U,S,C,T,W,j,A]=i.useMemo(()=>{let e=new o.WebGLRenderTarget(m,m),t=new o.WebGLRenderTarget(m,m);t.texture.generateMipmaps=e.texture.generateMipmaps=!1;let r=new o.PlaneGeometry(u,c).rotateX(Math.PI/2),n=new o.Mesh(r),i=new o.MeshDepthMaterial;i.depthTest=i.depthWrite=!1,i.onBeforeCompile=e=>{e.uniforms={...e.uniforms,ucolor:{value:new o.Color(p)}},e.fragmentShader=e.fragmentShader.replace("void main() {",`uniform vec3 ucolor;
           void main() {
          `),e.fragmentShader=e.fragmentShader.replace("vec4( vec3( 1.0 - fragCoordZ ), opacity );","vec4( ucolor * fragCoordZ * 2.0, ( 1.0 - fragCoordZ ) * 1.0 );")};let a=new o.ShaderMaterial(s),f=new o.ShaderMaterial(l);return f.depthTest=a.depthTest=!1,[e,r,i,n,a,f,t]},[m,u,c,e,p]),F=e=>{T.visible=!0,T.material=W,W.uniforms.tDiffuse.value=U.texture,W.uniforms.h.value=1*e/256,P.setRenderTarget(A),P.render(T,R.current),T.material=j,j.uniforms.tDiffuse.value=A.texture,j.uniforms.v.value=1*e/256,P.setRenderTarget(U),P.render(T,R.current),T.visible=!1},L=0;return(0,a.C)(()=>{R.current&&(t===1/0||L<t)&&(L++,w=E.background,b=E.overrideMaterial,D.current.visible=!1,E.background=null,E.overrideMaterial=C,P.setRenderTarget(U),P.render(E,R.current),F(f),h&&F(.4*f),P.setRenderTarget(null),D.current.visible=!0,E.overrideMaterial=b,E.background=w)}),i.useImperativeHandle(M,()=>D.current,[]),i.createElement("group",(0,n.Z)({"rotation-x":Math.PI/2},y,{ref:D}),i.createElement("mesh",{renderOrder:g,geometry:S,scale:[1,-1,1],rotation:[-Math.PI/2,0,0]},i.createElement("meshBasicMaterial",{transparent:!0,map:U.texture,opacity:r,depthWrite:x})),i.createElement("orthographicCamera",{ref:R,args:[-u/2,u/2,c/2,-c/2,d,v]}))})},2382:function(e,t,r){r.d(t,{i:function(){return l}});var n=r(1119),i=r(2265),o=r(1113),a=r(1448);let s=e=>"function"==typeof e,l=i.forwardRef(({envMap:e,resolution:t=256,frames:r=1/0,children:l,makeDefault:u,...c},f)=>{let d=(0,o.A)(({set:e})=>e),v=(0,o.A)(({camera:e})=>e),m=(0,o.A)(({size:e})=>e),h=i.useRef(null);i.useImperativeHandle(f,()=>h.current,[]);let p=i.useRef(null),x=function(e,t,r){let n=(0,o.A)(e=>e.size),s=(0,o.A)(e=>e.viewport),l="number"==typeof e?e:n.width*s.dpr,u=n.height*s.dpr,{samples:c=0,depth:f,...d}=("number"==typeof e?void 0:e)||{},v=i.useMemo(()=>{let e=new a.WebGLRenderTarget(l,u,{minFilter:a.LinearFilter,magFilter:a.LinearFilter,type:a.HalfFloatType,...d});return f&&(e.depthTexture=new a.DepthTexture(l,u,a.FloatType)),e.samples=c,e},[]);return i.useLayoutEffect(()=>{v.setSize(l,u),c&&(v.samples=c)},[c,v,l,u]),i.useEffect(()=>()=>v.dispose(),[]),v}(t);i.useLayoutEffect(()=>{c.manual||h.current.updateProjectionMatrix()},[m,c]),i.useLayoutEffect(()=>{h.current.updateProjectionMatrix()}),i.useLayoutEffect(()=>{if(u)return d(()=>({camera:h.current})),()=>d(()=>({camera:v}))},[h,u,d]);let g=0,y=null,M=s(l);return(0,o.C)(t=>{M&&(r===1/0||g<r)&&(p.current.visible=!1,t.gl.setRenderTarget(x),y=t.scene.background,e&&(t.scene.background=e),t.gl.render(t.scene,h.current),t.scene.background=y,t.gl.setRenderTarget(null),p.current.visible=!0,g++)}),i.createElement(i.Fragment,null,i.createElement("orthographicCamera",(0,n.Z)({left:-(m.width/2),right:m.width/2,top:m.height/2,bottom:-(m.height/2),ref:h},c),!M&&l),i.createElement("group",{ref:p},M&&l(x.texture)))})},8328:function(e,t,r){let n,i;r.d(t,{V:function(){return y}});var o=r(1119),a=r(2265),s=r(4040),l=r(1448),u=r(1113);let c=new l.Vector3,f=new l.Vector3,d=new l.Vector3,v=new l.Vector2;function m(e,t,r){let n=c.setFromMatrixPosition(e.matrixWorld);n.project(t);let i=r.width/2,o=r.height/2;return[n.x*i+i,-(n.y*o)+o]}let h=e=>1e-10>Math.abs(e)?0:e;function p(e,t,r=""){let n="matrix3d(";for(let r=0;16!==r;r++)n+=h(t[r]*e.elements[r])+(15!==r?",":")");return r+n}let x=(n=[1,-1,1,1,1,-1,1,1,1,-1,1,1,1,-1,1,1],e=>p(e,n)),g=(i=e=>[1/e,1/e,1/e,1,-1/e,-1/e,-1/e,-1,1/e,1/e,1/e,1,1,1,1,1],(e,t)=>p(e,i(t),"translate(-50%,-50%)")),y=a.forwardRef(({children:e,eps:t=.001,style:r,className:n,prepend:i,center:p,fullscreen:y,portal:M,distanceFactor:w,sprite:b=!1,transform:D=!1,occlude:E,onOcclude:P,castShadow:R,receiveShadow:U,material:S,geometry:C,zIndexRange:T=[16777271,0],calculatePosition:W=m,as:j="div",wrapperClass:A,pointerEvents:F="auto",...L},k)=>{let{gl:z,camera:I,scene:$,size:V,raycaster:_,events:O,viewport:H}=(0,u.A)(),[Z]=a.useState(()=>document.createElement(j)),N=a.useRef(),G=a.useRef(null),B=a.useRef(0),X=a.useRef([0,0]),q=a.useRef(null),J=a.useRef(null),K=(null==M?void 0:M.current)||O.connected||z.domElement.parentNode,Q=a.useRef(null),Y=a.useRef(!1),ee=a.useMemo(()=>{var e;return E&&"blending"!==E||Array.isArray(E)&&E.length&&(e=E[0])&&"object"==typeof e&&"current"in e},[E]);a.useLayoutEffect(()=>{let e=z.domElement;E&&"blending"===E?(e.style.zIndex=`${Math.floor(T[0]/2)}`,e.style.position="absolute",e.style.pointerEvents="none"):(e.style.zIndex=null,e.style.position=null,e.style.pointerEvents=null)},[E]),a.useLayoutEffect(()=>{if(G.current){let e=N.current=s.createRoot(Z);if($.updateMatrixWorld(),D)Z.style.cssText="position:absolute;top:0;left:0;pointer-events:none;overflow:hidden;";else{let e=W(G.current,I,V);Z.style.cssText=`position:absolute;top:0;left:0;transform:translate3d(${e[0]}px,${e[1]}px,0);transform-origin:0 0;`}return K&&(i?K.prepend(Z):K.appendChild(Z)),()=>{K&&K.removeChild(Z),e.unmount()}}},[K,D]),a.useLayoutEffect(()=>{A&&(Z.className=A)},[A]);let et=a.useMemo(()=>D?{position:"absolute",top:0,left:0,width:V.width,height:V.height,transformStyle:"preserve-3d",pointerEvents:"none"}:{position:"absolute",transform:p?"translate3d(-50%,-50%,0)":"none",...y&&{top:-V.height/2,left:-V.width/2,width:V.width,height:V.height},...r},[r,p,y,V,D]),er=a.useMemo(()=>({position:"absolute",pointerEvents:F}),[F]);a.useLayoutEffect(()=>{var t,i;Y.current=!1,D?null==(t=N.current)||t.render(a.createElement("div",{ref:q,style:et},a.createElement("div",{ref:J,style:er},a.createElement("div",{ref:k,className:n,style:r,children:e})))):null==(i=N.current)||i.render(a.createElement("div",{ref:k,style:et,className:n,children:e}))});let en=a.useRef(!0);(0,u.C)(e=>{if(G.current){I.updateMatrixWorld(),G.current.updateWorldMatrix(!0,!1);let e=D?X.current:W(G.current,I,V);if(D||Math.abs(B.current-I.zoom)>t||Math.abs(X.current[0]-e[0])>t||Math.abs(X.current[1]-e[1])>t){let t=function(e,t){let r=c.setFromMatrixPosition(e.matrixWorld),n=f.setFromMatrixPosition(t.matrixWorld),i=r.sub(n),o=t.getWorldDirection(d);return i.angleTo(o)>Math.PI/2}(G.current,I),r=!1;ee&&(Array.isArray(E)?r=E.map(e=>e.current):"blending"!==E&&(r=[$]));let n=en.current;if(r){let e=function(e,t,r,n){let i=c.setFromMatrixPosition(e.matrixWorld),o=i.clone();o.project(t),v.set(o.x,o.y),r.setFromCamera(v,t);let a=r.intersectObjects(n,!0);if(a.length){let e=a[0].distance;return i.distanceTo(r.ray.origin)<e}return!0}(G.current,I,_,r);en.current=e&&!t}else en.current=!t;n!==en.current&&(P?P(!en.current):Z.style.display=en.current?"block":"none");let i=Math.floor(T[0]/2),o=E?ee?[T[0],i]:[i-1,0]:T;if(Z.style.zIndex=`${function(e,t,r){if(t instanceof l.PerspectiveCamera||t instanceof l.OrthographicCamera){let n=c.setFromMatrixPosition(e.matrixWorld),i=f.setFromMatrixPosition(t.matrixWorld),o=n.distanceTo(i),a=(r[1]-r[0])/(t.far-t.near),s=r[1]-a*t.far;return Math.round(a*o+s)}}(G.current,I,o)}`,D){let[e,t]=[V.width/2,V.height/2],r=I.projectionMatrix.elements[5]*t,{isOrthographicCamera:n,top:i,left:o,bottom:a,right:s}=I,l=x(I.matrixWorldInverse),u=n?`scale(${r})translate(${h(-(s+o)/2)}px,${h((i+a)/2)}px)`:`translateZ(${r}px)`,c=G.current.matrixWorld;b&&((c=I.matrixWorldInverse.clone().transpose().copyPosition(c).scale(G.current.scale)).elements[3]=c.elements[7]=c.elements[11]=0,c.elements[15]=1),Z.style.width=V.width+"px",Z.style.height=V.height+"px",Z.style.perspective=n?"":`${r}px`,q.current&&J.current&&(q.current.style.transform=`${u}${l}translate(${e}px,${t}px)`,J.current.style.transform=g(c,1/((w||10)/400)))}else{let t=void 0===w?1:function(e,t){if(t instanceof l.OrthographicCamera)return t.zoom;if(!(t instanceof l.PerspectiveCamera))return 1;{let r=c.setFromMatrixPosition(e.matrixWorld),n=f.setFromMatrixPosition(t.matrixWorld);return 1/(2*Math.tan(t.fov*Math.PI/180/2)*r.distanceTo(n))}}(G.current,I)*w;Z.style.transform=`translate3d(${e[0]}px,${e[1]}px,0) scale(${t})`}X.current=e,B.current=I.zoom}}if(!ee&&Q.current&&!Y.current){if(D){if(q.current){let e=q.current.children[0];if(null!=e&&e.clientWidth&&null!=e&&e.clientHeight){let{isOrthographicCamera:t}=I;if(t||C)L.scale&&(Array.isArray(L.scale)?L.scale instanceof l.Vector3?Q.current.scale.copy(L.scale.clone().divideScalar(1)):Q.current.scale.set(1/L.scale[0],1/L.scale[1],1/L.scale[2]):Q.current.scale.setScalar(1/L.scale));else{let t=(w||10)/400,r=e.clientWidth*t,n=e.clientHeight*t;Q.current.scale.set(r,n,1)}Y.current=!0}}}else{let t=Z.children[0];if(null!=t&&t.clientWidth&&null!=t&&t.clientHeight){let e=1/H.factor,r=t.clientWidth*e,n=t.clientHeight*e;Q.current.scale.set(r,n,1),Y.current=!0}Q.current.lookAt(e.camera.position)}}});let ei=a.useMemo(()=>({vertexShader:D?void 0:`
          /*
            This shader is from the THREE's SpriteMaterial.
            We need to turn the backing plane into a Sprite
            (make it always face the camera) if "transfrom"
            is false.
          */
          #include <common>

          void main() {
            vec2 center = vec2(0., 1.);
            float rotation = 0.0;

            // This is somewhat arbitrary, but it seems to work well
            // Need to figure out how to derive this dynamically if it even matters
            float size = 0.03;

            vec4 mvPosition = modelViewMatrix * vec4( 0.0, 0.0, 0.0, 1.0 );
            vec2 scale;
            scale.x = length( vec3( modelMatrix[ 0 ].x, modelMatrix[ 0 ].y, modelMatrix[ 0 ].z ) );
            scale.y = length( vec3( modelMatrix[ 1 ].x, modelMatrix[ 1 ].y, modelMatrix[ 1 ].z ) );

            bool isPerspective = isPerspectiveMatrix( projectionMatrix );
            if ( isPerspective ) scale *= - mvPosition.z;

            vec2 alignedPosition = ( position.xy - ( center - vec2( 0.5 ) ) ) * scale * size;
            vec2 rotatedPosition;
            rotatedPosition.x = cos( rotation ) * alignedPosition.x - sin( rotation ) * alignedPosition.y;
            rotatedPosition.y = sin( rotation ) * alignedPosition.x + cos( rotation ) * alignedPosition.y;
            mvPosition.xy += rotatedPosition;

            gl_Position = projectionMatrix * mvPosition;
          }
      `,fragmentShader:`
        void main() {
          gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
        }
      `}),[D]);return a.createElement("group",(0,o.Z)({},L,{ref:G}),E&&!ee&&a.createElement("mesh",{castShadow:R,receiveShadow:U,ref:Q},C||a.createElement("planeGeometry",null),S||a.createElement("shaderMaterial",{side:l.DoubleSide,vertexShader:ei.vertexShader,fragmentShader:ei.fragmentShader})))})},9148:function(e,t,r){r.d(t,{Z:function(){return o}});var n=r(2265);let i="undefined"==typeof window||!window.navigator||/ServerSideRendering|^Deno\//.test(window.navigator.userAgent)?n.useEffect:n.useLayoutEffect;function o(e){let t="function"==typeof e?function(e){let t;let r=new Set,n=(e,n)=>{let i="function"==typeof e?e(t):e;if(i!==t){let e=t;t=n?i:Object.assign({},t,i),r.forEach(r=>r(t,e))}},i=()=>t,o=(e,n=i,o=Object.is)=>{console.warn("[DEPRECATED] Please use `subscribeWithSelector` middleware");let a=n(t);function s(){let r=n(t);if(!o(a,r)){let t=a;e(a=r,t)}}return r.add(s),()=>r.delete(s)},a={setState:n,getState:i,subscribe:(e,t,n)=>t||n?o(e,t,n):(r.add(e),()=>r.delete(e)),destroy:()=>r.clear()};return t=e(n,i,a),a}(e):e,r=(e=t.getState,r=Object.is)=>{let o;let[,a]=(0,n.useReducer)(e=>e+1,0),s=t.getState(),l=(0,n.useRef)(s),u=(0,n.useRef)(e),c=(0,n.useRef)(r),f=(0,n.useRef)(!1),d=(0,n.useRef)();void 0===d.current&&(d.current=e(s));let v=!1;(l.current!==s||u.current!==e||c.current!==r||f.current)&&(o=e(s),v=!r(d.current,o)),i(()=>{v&&(d.current=o),l.current=s,u.current=e,c.current=r,f.current=!1});let m=(0,n.useRef)(s);i(()=>{let e=()=>{try{let e=t.getState(),r=u.current(e);c.current(d.current,r)||(l.current=e,d.current=r,a())}catch(e){f.current=!0,a()}},r=t.subscribe(e);return t.getState()!==m.current&&e(),r},[]);let h=v?o:d.current;return(0,n.useDebugValue)(h),h};return Object.assign(r,t),r[Symbol.iterator]=function(){console.warn("[useStore, api] = create() is deprecated and will be removed in v4");let e=[r,t];return{next(){let t=e.length<=0;return{value:e.shift(),done:t}}}},r}},8614:function(e,t,r){r.d(t,{M:function(){return x}});var n=r(7437),i=r(2265),o=r(8881),a=r(3576),s=r(4252),l=r(5750);class u extends i.Component{getSnapshotBeforeUpdate(e){let t=this.props.childRef.current;if(t&&e.isPresent&&!this.props.isPresent){let e=this.props.sizeRef.current;e.height=t.offsetHeight||0,e.width=t.offsetWidth||0,e.top=t.offsetTop,e.left=t.offsetLeft}return null}componentDidUpdate(){}render(){return this.props.children}}function c(e){let{children:t,isPresent:r}=e,o=(0,i.useId)(),a=(0,i.useRef)(null),s=(0,i.useRef)({width:0,height:0,top:0,left:0}),{nonce:c}=(0,i.useContext)(l._);return(0,i.useInsertionEffect)(()=>{let{width:e,height:t,top:n,left:i}=s.current;if(r||!a.current||!e||!t)return;a.current.dataset.motionPopId=o;let l=document.createElement("style");return c&&(l.nonce=c),document.head.appendChild(l),l.sheet&&l.sheet.insertRule('\n          [data-motion-pop-id="'.concat(o,'"] {\n            position: absolute !important;\n            width: ').concat(e,"px !important;\n            height: ").concat(t,"px !important;\n            top: ").concat(n,"px !important;\n            left: ").concat(i,"px !important;\n          }\n        ")),()=>{document.head.removeChild(l)}},[r]),(0,n.jsx)(u,{isPresent:r,childRef:a,sizeRef:s,children:i.cloneElement(t,{ref:a})})}let f=e=>{let{children:t,initial:r,isPresent:o,onExitComplete:l,custom:u,presenceAffectsLayout:f,mode:v}=e,m=(0,a.h)(d),h=(0,i.useId)(),p=(0,i.useCallback)(e=>{for(let t of(m.set(e,!0),m.values()))if(!t)return;l&&l()},[m,l]),x=(0,i.useMemo)(()=>({id:h,initial:r,isPresent:o,custom:u,onExitComplete:p,register:e=>(m.set(e,!1),()=>m.delete(e))}),f?[Math.random(),p]:[o,p]);return(0,i.useMemo)(()=>{m.forEach((e,t)=>m.set(t,!1))},[o]),i.useEffect(()=>{o||m.size||!l||l()},[o]),"popLayout"===v&&(t=(0,n.jsx)(c,{isPresent:o,children:t})),(0,n.jsx)(s.O.Provider,{value:x,children:t})};function d(){return new Map}var v=r(9637);let m=e=>e.key||"";function h(e){let t=[];return i.Children.forEach(e,e=>{(0,i.isValidElement)(e)&&t.push(e)}),t}var p=r(1534);let x=e=>{let{children:t,custom:r,initial:s=!0,onExitComplete:l,presenceAffectsLayout:u=!0,mode:c="sync",propagate:d=!1}=e,[x,g]=(0,v.oO)(d),y=(0,i.useMemo)(()=>h(t),[t]),M=d&&!x?[]:y.map(m),w=(0,i.useRef)(!0),b=(0,i.useRef)(y),D=(0,a.h)(()=>new Map),[E,P]=(0,i.useState)(y),[R,U]=(0,i.useState)(y);(0,p.L)(()=>{w.current=!1,b.current=y;for(let e=0;e<R.length;e++){let t=m(R[e]);M.includes(t)?D.delete(t):!0!==D.get(t)&&D.set(t,!1)}},[R,M.length,M.join("-")]);let S=[];if(y!==E){let e=[...y];for(let t=0;t<R.length;t++){let r=R[t],n=m(r);M.includes(n)||(e.splice(t,0,r),S.push(r))}"wait"===c&&S.length&&(e=S),U(h(e)),P(y);return}let{forceRender:C}=(0,i.useContext)(o.p);return(0,n.jsx)(n.Fragment,{children:R.map(e=>{let t=m(e),i=(!d||!!x)&&(y===R||M.includes(t));return(0,n.jsx)(f,{isPresent:i,initial:(!w.current||!!s)&&void 0,custom:i?void 0:r,presenceAffectsLayout:u,mode:c,onExitComplete:i?void 0:()=>{if(!D.has(t))return;D.set(t,!0);let e=!0;D.forEach(t=>{t||(e=!1)}),e&&(null==C||C(),U(b.current),d&&(null==g||g()),l&&l())},children:e},t)})})}}}]);