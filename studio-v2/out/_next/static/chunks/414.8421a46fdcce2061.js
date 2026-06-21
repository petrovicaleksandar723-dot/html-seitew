"use strict";(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[414],{1057:function(e,t,r){r.d(t,{j:function(){return u}});var n=r(1119),i=r(2265),o=r(1448),a=r(9563);let s={uniforms:{tDiffuse:{value:null},h:{value:1/512}},vertexShader:`
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
  `},u=i.forwardRef(({scale:e=10,frames:t=1/0,opacity:r=1,width:u=1,height:c=1,blur:f=1,near:v=0,far:d=10,resolution:m=512,smooth:h=!0,color:p="#000000",depthWrite:x=!1,renderOrder:g,...y},M)=>{let w,D;let P=i.useRef(null),b=(0,a.A)(e=>e.scene),E=(0,a.A)(e=>e.gl),U=i.useRef(null);u*=Array.isArray(e)?e[0]:e||1,c*=Array.isArray(e)?e[1]:e||1;let[R,C,S,T,W,A,F]=i.useMemo(()=>{let e=new o.WebGLRenderTarget(m,m),t=new o.WebGLRenderTarget(m,m);t.texture.generateMipmaps=e.texture.generateMipmaps=!1;let r=new o.PlaneGeometry(u,c).rotateX(Math.PI/2),n=new o.Mesh(r),i=new o.MeshDepthMaterial;i.depthTest=i.depthWrite=!1,i.onBeforeCompile=e=>{e.uniforms={...e.uniforms,ucolor:{value:new o.Color(p)}},e.fragmentShader=e.fragmentShader.replace("void main() {",`uniform vec3 ucolor;
           void main() {
          `),e.fragmentShader=e.fragmentShader.replace("vec4( vec3( 1.0 - fragCoordZ ), opacity );","vec4( ucolor * fragCoordZ * 2.0, ( 1.0 - fragCoordZ ) * 1.0 );")};let a=new o.ShaderMaterial(s),f=new o.ShaderMaterial(l);return f.depthTest=a.depthTest=!1,[e,r,i,n,a,f,t]},[m,u,c,e,p]),j=e=>{T.visible=!0,T.material=W,W.uniforms.tDiffuse.value=R.texture,W.uniforms.h.value=1*e/256,E.setRenderTarget(F),E.render(T,U.current),T.material=A,A.uniforms.tDiffuse.value=F.texture,A.uniforms.v.value=1*e/256,E.setRenderTarget(R),E.render(T,U.current),T.visible=!1},k=0;return(0,a.C)(()=>{U.current&&(t===1/0||k<t)&&(k++,w=b.background,D=b.overrideMaterial,P.current.visible=!1,b.background=null,b.overrideMaterial=S,E.setRenderTarget(R),E.render(b,U.current),j(f),h&&j(.4*f),E.setRenderTarget(null),P.current.visible=!0,b.overrideMaterial=D,b.background=w)}),i.useImperativeHandle(M,()=>P.current,[]),i.createElement("group",(0,n.Z)({"rotation-x":Math.PI/2},y,{ref:P}),i.createElement("mesh",{renderOrder:g,geometry:C,scale:[1,-1,1],rotation:[-Math.PI/2,0,0]},i.createElement("meshBasicMaterial",{transparent:!0,map:R.texture,opacity:r,depthWrite:x})),i.createElement("orthographicCamera",{ref:U,args:[-u/2,u/2,c/2,-c/2,v,d]}))})},2382:function(e,t,r){r.d(t,{i:function(){return l}});var n=r(1119),i=r(2265),o=r(9563),a=r(1448);let s=e=>"function"==typeof e,l=i.forwardRef(({envMap:e,resolution:t=256,frames:r=1/0,children:l,makeDefault:u,...c},f)=>{let v=(0,o.A)(({set:e})=>e),d=(0,o.A)(({camera:e})=>e),m=(0,o.A)(({size:e})=>e),h=i.useRef(null);i.useImperativeHandle(f,()=>h.current,[]);let p=i.useRef(null),x=function(e,t,r){let n=(0,o.A)(e=>e.size),s=(0,o.A)(e=>e.viewport),l="number"==typeof e?e:n.width*s.dpr,u=n.height*s.dpr,{samples:c=0,depth:f,...v}=("number"==typeof e?void 0:e)||{},d=i.useMemo(()=>{let e=new a.WebGLRenderTarget(l,u,{minFilter:a.LinearFilter,magFilter:a.LinearFilter,type:a.HalfFloatType,...v});return f&&(e.depthTexture=new a.DepthTexture(l,u,a.FloatType)),e.samples=c,e},[]);return i.useLayoutEffect(()=>{d.setSize(l,u),c&&(d.samples=c)},[c,d,l,u]),i.useEffect(()=>()=>d.dispose(),[]),d}(t);i.useLayoutEffect(()=>{c.manual||h.current.updateProjectionMatrix()},[m,c]),i.useLayoutEffect(()=>{h.current.updateProjectionMatrix()}),i.useLayoutEffect(()=>{if(u)return v(()=>({camera:h.current})),()=>v(()=>({camera:d}))},[h,u,v]);let g=0,y=null,M=s(l);return(0,o.C)(t=>{M&&(r===1/0||g<r)&&(p.current.visible=!1,t.gl.setRenderTarget(x),y=t.scene.background,e&&(t.scene.background=e),t.gl.render(t.scene,h.current),t.scene.background=y,t.gl.setRenderTarget(null),p.current.visible=!0,g++)}),i.createElement(i.Fragment,null,i.createElement("orthographicCamera",(0,n.Z)({left:-(m.width/2),right:m.width/2,top:m.height/2,bottom:-(m.height/2),ref:h},c),!M&&l),i.createElement("group",{ref:p},M&&l(x.texture)))})},8328:function(e,t,r){let n,i;r.d(t,{V:function(){return y}});var o=r(1119),a=r(2265),s=r(4040),l=r(1448),u=r(9563);let c=new l.Vector3,f=new l.Vector3,v=new l.Vector3,d=new l.Vector2;function m(e,t,r){let n=c.setFromMatrixPosition(e.matrixWorld);n.project(t);let i=r.width/2,o=r.height/2;return[n.x*i+i,-(n.y*o)+o]}let h=e=>1e-10>Math.abs(e)?0:e;function p(e,t,r=""){let n="matrix3d(";for(let r=0;16!==r;r++)n+=h(t[r]*e.elements[r])+(15!==r?",":")");return r+n}let x=(n=[1,-1,1,1,1,-1,1,1,1,-1,1,1,1,-1,1,1],e=>p(e,n)),g=(i=e=>[1/e,1/e,1/e,1,-1/e,-1/e,-1/e,-1,1/e,1/e,1/e,1,1,1,1,1],(e,t)=>p(e,i(t),"translate(-50%,-50%)")),y=a.forwardRef(({children:e,eps:t=.001,style:r,className:n,prepend:i,center:p,fullscreen:y,portal:M,distanceFactor:w,sprite:D=!1,transform:P=!1,occlude:b,onOcclude:E,castShadow:U,receiveShadow:R,material:C,geometry:S,zIndexRange:T=[16777271,0],calculatePosition:W=m,as:A="div",wrapperClass:F,pointerEvents:j="auto",...k},L)=>{let{gl:z,camera:I,scene:$,size:_,raycaster:V,events:H,viewport:N}=(0,u.A)(),[Z]=a.useState(()=>document.createElement(A)),O=a.useRef(),G=a.useRef(null),B=a.useRef(0),X=a.useRef([0,0]),q=a.useRef(null),J=a.useRef(null),K=(null==M?void 0:M.current)||H.connected||z.domElement.parentNode,Q=a.useRef(null),Y=a.useRef(!1),ee=a.useMemo(()=>{var e;return b&&"blending"!==b||Array.isArray(b)&&b.length&&(e=b[0])&&"object"==typeof e&&"current"in e},[b]);a.useLayoutEffect(()=>{let e=z.domElement;b&&"blending"===b?(e.style.zIndex=`${Math.floor(T[0]/2)}`,e.style.position="absolute",e.style.pointerEvents="none"):(e.style.zIndex=null,e.style.position=null,e.style.pointerEvents=null)},[b]),a.useLayoutEffect(()=>{if(G.current){let e=O.current=s.createRoot(Z);if($.updateMatrixWorld(),P)Z.style.cssText="position:absolute;top:0;left:0;pointer-events:none;overflow:hidden;";else{let e=W(G.current,I,_);Z.style.cssText=`position:absolute;top:0;left:0;transform:translate3d(${e[0]}px,${e[1]}px,0);transform-origin:0 0;`}return K&&(i?K.prepend(Z):K.appendChild(Z)),()=>{K&&K.removeChild(Z),e.unmount()}}},[K,P]),a.useLayoutEffect(()=>{F&&(Z.className=F)},[F]);let et=a.useMemo(()=>P?{position:"absolute",top:0,left:0,width:_.width,height:_.height,transformStyle:"preserve-3d",pointerEvents:"none"}:{position:"absolute",transform:p?"translate3d(-50%,-50%,0)":"none",...y&&{top:-_.height/2,left:-_.width/2,width:_.width,height:_.height},...r},[r,p,y,_,P]),er=a.useMemo(()=>({position:"absolute",pointerEvents:j}),[j]);a.useLayoutEffect(()=>{var t,i;Y.current=!1,P?null==(t=O.current)||t.render(a.createElement("div",{ref:q,style:et},a.createElement("div",{ref:J,style:er},a.createElement("div",{ref:L,className:n,style:r,children:e})))):null==(i=O.current)||i.render(a.createElement("div",{ref:L,style:et,className:n,children:e}))});let en=a.useRef(!0);(0,u.C)(e=>{if(G.current){I.updateMatrixWorld(),G.current.updateWorldMatrix(!0,!1);let e=P?X.current:W(G.current,I,_);if(P||Math.abs(B.current-I.zoom)>t||Math.abs(X.current[0]-e[0])>t||Math.abs(X.current[1]-e[1])>t){let t=function(e,t){let r=c.setFromMatrixPosition(e.matrixWorld),n=f.setFromMatrixPosition(t.matrixWorld),i=r.sub(n),o=t.getWorldDirection(v);return i.angleTo(o)>Math.PI/2}(G.current,I),r=!1;ee&&(Array.isArray(b)?r=b.map(e=>e.current):"blending"!==b&&(r=[$]));let n=en.current;if(r){let e=function(e,t,r,n){let i=c.setFromMatrixPosition(e.matrixWorld),o=i.clone();o.project(t),d.set(o.x,o.y),r.setFromCamera(d,t);let a=r.intersectObjects(n,!0);if(a.length){let e=a[0].distance;return i.distanceTo(r.ray.origin)<e}return!0}(G.current,I,V,r);en.current=e&&!t}else en.current=!t;n!==en.current&&(E?E(!en.current):Z.style.display=en.current?"block":"none");let i=Math.floor(T[0]/2),o=b?ee?[T[0],i]:[i-1,0]:T;if(Z.style.zIndex=`${function(e,t,r){if(t instanceof l.PerspectiveCamera||t instanceof l.OrthographicCamera){let n=c.setFromMatrixPosition(e.matrixWorld),i=f.setFromMatrixPosition(t.matrixWorld),o=n.distanceTo(i),a=(r[1]-r[0])/(t.far-t.near),s=r[1]-a*t.far;return Math.round(a*o+s)}}(G.current,I,o)}`,P){let[e,t]=[_.width/2,_.height/2],r=I.projectionMatrix.elements[5]*t,{isOrthographicCamera:n,top:i,left:o,bottom:a,right:s}=I,l=x(I.matrixWorldInverse),u=n?`scale(${r})translate(${h(-(s+o)/2)}px,${h((i+a)/2)}px)`:`translateZ(${r}px)`,c=G.current.matrixWorld;D&&((c=I.matrixWorldInverse.clone().transpose().copyPosition(c).scale(G.current.scale)).elements[3]=c.elements[7]=c.elements[11]=0,c.elements[15]=1),Z.style.width=_.width+"px",Z.style.height=_.height+"px",Z.style.perspective=n?"":`${r}px`,q.current&&J.current&&(q.current.style.transform=`${u}${l}translate(${e}px,${t}px)`,J.current.style.transform=g(c,1/((w||10)/400)))}else{let t=void 0===w?1:function(e,t){if(t instanceof l.OrthographicCamera)return t.zoom;if(!(t instanceof l.PerspectiveCamera))return 1;{let r=c.setFromMatrixPosition(e.matrixWorld),n=f.setFromMatrixPosition(t.matrixWorld);return 1/(2*Math.tan(t.fov*Math.PI/180/2)*r.distanceTo(n))}}(G.current,I)*w;Z.style.transform=`translate3d(${e[0]}px,${e[1]}px,0) scale(${t})`}X.current=e,B.current=I.zoom}}if(!ee&&Q.current&&!Y.current){if(P){if(q.current){let e=q.current.children[0];if(null!=e&&e.clientWidth&&null!=e&&e.clientHeight){let{isOrthographicCamera:t}=I;if(t||S)k.scale&&(Array.isArray(k.scale)?k.scale instanceof l.Vector3?Q.current.scale.copy(k.scale.clone().divideScalar(1)):Q.current.scale.set(1/k.scale[0],1/k.scale[1],1/k.scale[2]):Q.current.scale.setScalar(1/k.scale));else{let t=(w||10)/400,r=e.clientWidth*t,n=e.clientHeight*t;Q.current.scale.set(r,n,1)}Y.current=!0}}}else{let t=Z.children[0];if(null!=t&&t.clientWidth&&null!=t&&t.clientHeight){let e=1/N.factor,r=t.clientWidth*e,n=t.clientHeight*e;Q.current.scale.set(r,n,1),Y.current=!0}Q.current.lookAt(e.camera.position)}}});let ei=a.useMemo(()=>({vertexShader:P?void 0:`
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
      `}),[P]);return a.createElement("group",(0,o.Z)({},k,{ref:G}),b&&!ee&&a.createElement("mesh",{castShadow:U,receiveShadow:R,ref:Q},S||a.createElement("planeGeometry",null),C||a.createElement("shaderMaterial",{side:l.DoubleSide,vertexShader:ei.vertexShader,fragmentShader:ei.fragmentShader})))})},8614:function(e,t,r){r.d(t,{M:function(){return x}});var n=r(7437),i=r(2265),o=r(8881),a=r(3576),s=r(4252),l=r(5750);class u extends i.Component{getSnapshotBeforeUpdate(e){let t=this.props.childRef.current;if(t&&e.isPresent&&!this.props.isPresent){let e=this.props.sizeRef.current;e.height=t.offsetHeight||0,e.width=t.offsetWidth||0,e.top=t.offsetTop,e.left=t.offsetLeft}return null}componentDidUpdate(){}render(){return this.props.children}}function c(e){let{children:t,isPresent:r}=e,o=(0,i.useId)(),a=(0,i.useRef)(null),s=(0,i.useRef)({width:0,height:0,top:0,left:0}),{nonce:c}=(0,i.useContext)(l._);return(0,i.useInsertionEffect)(()=>{let{width:e,height:t,top:n,left:i}=s.current;if(r||!a.current||!e||!t)return;a.current.dataset.motionPopId=o;let l=document.createElement("style");return c&&(l.nonce=c),document.head.appendChild(l),l.sheet&&l.sheet.insertRule('\n          [data-motion-pop-id="'.concat(o,'"] {\n            position: absolute !important;\n            width: ').concat(e,"px !important;\n            height: ").concat(t,"px !important;\n            top: ").concat(n,"px !important;\n            left: ").concat(i,"px !important;\n          }\n        ")),()=>{document.head.removeChild(l)}},[r]),(0,n.jsx)(u,{isPresent:r,childRef:a,sizeRef:s,children:i.cloneElement(t,{ref:a})})}let f=e=>{let{children:t,initial:r,isPresent:o,onExitComplete:l,custom:u,presenceAffectsLayout:f,mode:d}=e,m=(0,a.h)(v),h=(0,i.useId)(),p=(0,i.useCallback)(e=>{for(let t of(m.set(e,!0),m.values()))if(!t)return;l&&l()},[m,l]),x=(0,i.useMemo)(()=>({id:h,initial:r,isPresent:o,custom:u,onExitComplete:p,register:e=>(m.set(e,!1),()=>m.delete(e))}),f?[Math.random(),p]:[o,p]);return(0,i.useMemo)(()=>{m.forEach((e,t)=>m.set(t,!1))},[o]),i.useEffect(()=>{o||m.size||!l||l()},[o]),"popLayout"===d&&(t=(0,n.jsx)(c,{isPresent:o,children:t})),(0,n.jsx)(s.O.Provider,{value:x,children:t})};function v(){return new Map}var d=r(9637);let m=e=>e.key||"";function h(e){let t=[];return i.Children.forEach(e,e=>{(0,i.isValidElement)(e)&&t.push(e)}),t}var p=r(1534);let x=e=>{let{children:t,custom:r,initial:s=!0,onExitComplete:l,presenceAffectsLayout:u=!0,mode:c="sync",propagate:v=!1}=e,[x,g]=(0,d.oO)(v),y=(0,i.useMemo)(()=>h(t),[t]),M=v&&!x?[]:y.map(m),w=(0,i.useRef)(!0),D=(0,i.useRef)(y),P=(0,a.h)(()=>new Map),[b,E]=(0,i.useState)(y),[U,R]=(0,i.useState)(y);(0,p.L)(()=>{w.current=!1,D.current=y;for(let e=0;e<U.length;e++){let t=m(U[e]);M.includes(t)?P.delete(t):!0!==P.get(t)&&P.set(t,!1)}},[U,M.length,M.join("-")]);let C=[];if(y!==b){let e=[...y];for(let t=0;t<U.length;t++){let r=U[t],n=m(r);M.includes(n)||(e.splice(t,0,r),C.push(r))}"wait"===c&&C.length&&(e=C),R(h(e)),E(y);return}let{forceRender:S}=(0,i.useContext)(o.p);return(0,n.jsx)(n.Fragment,{children:U.map(e=>{let t=m(e),i=(!v||!!x)&&(y===U||M.includes(t));return(0,n.jsx)(f,{isPresent:i,initial:(!w.current||!!s)&&void 0,custom:i?void 0:r,presenceAffectsLayout:u,mode:c,onExitComplete:i?void 0:()=>{if(!P.has(t))return;P.set(t,!0);let e=!0;P.forEach(t=>{t||(e=!1)}),e&&(null==S||S(),R(D.current),v&&(null==g||g()),l&&l())},children:e},t)})})}}}]);