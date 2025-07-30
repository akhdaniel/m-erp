<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="text-center">
      <h1 class="text-6xl font-bold text-gray-900">404</h1>
      <h2 class="mt-4 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
        Page not found
      </h2>
      <p class="mt-6 text-lg leading-7 text-gray-600">
        Sorry, we couldn't find the page you're looking for.
      </p>
      <div class="mt-10">
        <router-link
          to="/dashboard"
          class="btn btn-primary"
        >
          Go back home
        </router-link>
      </div>
    </div>
  </div>
</template>